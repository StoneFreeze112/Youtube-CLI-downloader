import os
import subprocess
import sys
import re
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def check_dependencies():
    print("Checking for dependencies...")
    dependencies = ['yt-dlp', 'ffmpeg', 'aria2c']
    missing = []

    for dep in dependencies:
        command = 'where' if os.name == 'nt' else 'which'
        if subprocess.call([command, dep], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) != 0:
            missing.append(dep)

    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        choice = input("Do you want to install the missing dependencies automatically? (y/n): ").strip().lower()
        if choice == 'y':
            try:
                for dep in missing:
                    if os.name == 'nt':
                        subprocess.check_call(["choco", "install", dep, "-y"])
                    else:
                        subprocess.check_call(["sudo", "apt-get", "install", dep, "-y"])
                print("Dependencies installed successfully. Please restart the script.")
            except Exception as e:
                print(f"Error installing dependencies: {str(e)}")
                sys.exit(1)
        else:
            print("Please install the missing dependencies and try again.")
            sys.exit(1)
    else:
        print("All dependencies are installed.")

def get_youtube_url():
    url = input("Enter the YouTube link: ").strip()
    if not url or not re.match(r'(https?://)?(www\.)?(youtube|youtu\.be)', url):
        print("Invalid URL. Please provide a valid YouTube link.")
        sys.exit(1)
    return url

def choose_format():
    print("Choose the format:")
    print("[1] Best Quality Video (1080p)")
    print("[2] Good Quality Video (720p)")
    print("[3] Fine Quality Video (480p)")
    print("[4] Best Audio (MP3)")

    choice = input("Enter the number corresponding to the format (1, 2, 3, or 4): ").strip()

    format_dict = {
        '1': 'bestvideo[height<=1080]/best[height<=1080]',
        '2': 'bestvideo[height<=720]/best[height<=720]',
        '3': 'bestvideo[height<=480]/best[height<=480]',
        '4': 'bestaudio'
    }

    if choice in format_dict:
        return format_dict[choice]
    else:
        print("Invalid choice! Please enter '1', '2', '3', or '4'.")
        sys.exit(1)

def download_video(url, format_type, retries=3):
    logger.info("Preparing to download...")

    # Define output directories
    video_dir = os.path.expanduser('~/Downloads/YouTube Videos')
    audio_dir = os.path.expanduser('~/Downloads/YouTube Music')
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    output_template = os.path.join(video_dir if format_type.startswith("bestvideo") else audio_dir, '%(title)s.%(ext)s')

    command = [
        'yt-dlp',
        '-f', format_type,
        '--write-thumbnail', '-o', output_template,
        '--external-downloader', 'aria2c',
        '--external-downloader-args', '-x 16 -s 16 -k 1M',
        url
    ]

    for attempt in range(retries + 1):
        logger.info(f"Download attempt {attempt + 1}...")
        try:
            subprocess.run(command, check=True)
            logger.info(f"Download completed successfully. Saved to: {output_template}")
            return
        except subprocess.CalledProcessError as e:
            logger.error(f"Download error: {str(e)}")
            if attempt == retries:
                logger.error(f"Download failed after {retries + 1} attempts.")
                return

    logger.error("Download failed.")

def main():
    # Check if dependencies are installed
    check_dependencies()

    # Get the YouTube link and format choice from the user
    url = get_youtube_url()
    format_type = choose_format()

    # Call the download function
    download_video(url, format_type)

if __name__ == '__main__':
    main()
