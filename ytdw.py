import os
import re
import requests
import subprocess
import logging
from urllib.parse import unquote, urlsplit

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_filename(filename):
    """ Sanitize filename by removing invalid characters for different OSes. """
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def get_filename_from_url(url):
    """ Get the filename from URL or headers. """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.head(url, allow_redirects=True, headers=headers)

        # Check for filename in 'Content-Disposition'
        filename = re.findall(r'filename\*=UTF-8\'\'(.+)', response.headers.get('Content-Disposition', '')) or \
                   re.findall(r'filename="(.+)"', response.headers.get('Content-Disposition', ''))
        if filename:
            return sanitize_filename(unquote(filename[0]))

        # Fall back to the URL path
        path = urlsplit(response.url).path
        filename = os.path.basename(path)
        return sanitize_filename(unquote(filename)) if filename else "downloaded_file"

    except requests.RequestException as e:
        logging.error(f"Error fetching filename: {e}")
    return "downloaded_file"

def get_file_size(url):
    """ Get the file size from the URL. """
    try:
        response = requests.head(url, allow_redirects=True)
        return int(response.headers.get('Content-Length', 0))
    except requests.RequestException as e:
        logging.error(f"Error fetching file size: {e}")
    return 0

def determine_segments(file_size):
    """ Determine the number of segments based on file size. """
    if file_size == 0:
        return 1  # Default to 1 segment if file size is unknown
    
    # More by default for large files, allow dynamic allocation
    return 30  # Set maximum to a very high number for practical purposes

def get_connection_count():
    """ Get user-defined connection count, ensuring it is between 8 and 32. """
    try:
        count = int(input("Enter number of connections (8 to 32, default: 8): ").strip() or 8)
        if count < 8 or count > 32:
            logging.warning("Invalid number of connections. Setting to default (8).")
            count = 8
        return count
    except ValueError:
        logging.warning("Invalid input for connections. Setting to default (8).")
        return 8

def download_with_aria2c(url, download_path):
    """ Download file using aria2c. """
    filename = get_filename_from_url(url)

    os.makedirs(download_path, exist_ok=True)
    file_path = os.path.join(download_path, filename)

    file_size = get_file_size(url)
    num_segments = determine_segments(file_size)
    connection_count = get_connection_count()
    logging.info(f"File Size: {file_size / (1024 * 1024):.2f} MB, Estimated Segments: {num_segments}")
    logging.info(f"Using {connection_count} connections per server.")

    # Constructing the aria2c command
    command = [
        "aria2c",
        url,
        "--out", filename,
        "--dir", download_path,
        "--check-certificate=false",
        f"--split={num_segments}",
        f"--max-connection-per-server={connection_count}",  # Set user-defined connection count
        "--min-split-size=1M",  # Minimum split size for download chunks
        "--enable-http-pipelining=true",  # Enable HTTP/2 pipelining, if supported
        "--file-allocation=trunc"
    ]

    try:
        logging.info("Checking aria2c installation...")
        subprocess.run(["aria2c", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(f"Starting download with aria2c... Command: {' '.join(command)}")
        subprocess.run(command, check=True)
        logging.info(f"Download completed: {file_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Download failed: {e}")

if __name__ == "__main__":
    download_url = input("Enter the download URL: ").strip()
    if not re.match(r'http[s]?://', download_url):
        logging.error("Invalid URL provided. Please enter a valid URL.")
    else:
        download_location = input("Enter the download location path (default: 'LXDM'): ").strip() or "LXDM"
        download_with_aria2c(download_url, download_location)
