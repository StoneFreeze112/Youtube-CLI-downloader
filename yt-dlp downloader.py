import os
import subprocess
import sys

def check_dependencies():
    dependencies = ['yt-dlp', 'ffmpeg']
    missing = []

    for dep in dependencies:
        if subprocess.call(['which', dep], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) != 0:
            missing.append(dep)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Please install the missing dependencies and try again.")
        sys.exit(1)

def download_video(url, format_type, resolution):
    # Define the output directory
    output_dir = os.path.expanduser('~/Downloads/YouTube Videos')
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

    # Set the output file name
    if format_type == 'mp4':
        output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
        command = [
            'yt-dlp',
            '-f', f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
            '--merge-output-format', 'mp4',
            '--embed-thumbnail',
            '-o', output_template,
            url
        ]
    elif format_type == 'mp3':
        output_template = os.path.join(output_dir, '%(title)s.mp3')
        command = [
            'yt-dlp',
            '-f', 'bestaudio',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--embed-thumbnail',
            '-o', output_template,
            url
        ]

    # Run the command
    try:
        print("Starting download... This might take a while.")
        subprocess.run(command, check=True)
        print(f"Download completed successfully and saved to {output_dir}")
    except subprocess.CalledProcessError:
        print("An error occurred during the download. Please check the URL or your internet connection.")

def main():
    # Check if dependencies are installed
    check_dependencies()

    # Get the YouTube link from the user
    url = input("Enter the YouTube link: ").strip()
    if not url:
        print("URL cannot be empty.")
        sys.exit(1)
    
    # Ask for format using numbered options
    print("Choose the format:")
    print("[1] MP4")
    print("[2] MP3")
    format_choice = input("Enter the number corresponding to the format (1 or 2): ").strip()

    if format_choice == '1':
        format_type = 'mp4'
    elif format_choice == '2':
        format_type = 'mp3'
    else:
        print("Invalid choice! Please enter '1' for MP4 or '2' for MP3.")
        sys.exit(1)

    # Ask for resolution or quality
    if format_type == 'mp4':
        resolution = input("Enter the desired resolution (e.g., 720, 1080): ").strip()
        if not resolution.isdigit():
            print("Invalid resolution! Please enter a number.")
            sys.exit(1)
    else:
        resolution = input("Enter the desired audio quality (e.g., 128K, 192K): ").strip()

    # Call the download function
    download_video(url, format_type, resolution)

if __name__ == '__main__':
    main()
