import os
import subprocess
import sys

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
        print("Please install the missing dependencies and try again.")
        sys.exit(1)
    else:
        print("All dependencies are installed.")

def download_video(url, format_type, quality):
    print("Preparing to download...")
    # Define the output directories
    video_dir = os.path.expanduser('~/Downloads/YouTube Videos')
    audio_dir = os.path.expanduser('~/Downloads/YouTube Music')
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    if format_type == 'mp4':
        output_template = os.path.join(video_dir, '%(title)s.%(ext)s')
        
        if quality == 'best':
            video_format = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
        elif quality == 'good':
            video_format = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
        else:  # Fine quality
            video_format = 'bestvideo[height<=480]+bestaudio/best[height<=480]'

        command = [
            'yt-dlp',
            '-f', video_format,
            '--merge-output-format', 'mp4',
            '--embed-thumbnail',
            '-o', output_template,
            '--external-downloader', 'aria2c',
            '--external-downloader-args', '-x 16 -s 16 -k 1M',
            url
        ]
    elif format_type == 'mp3':
        output_template = os.path.join(audio_dir, '%(title)s.mp3')
        command = [
            'yt-dlp',
            '-f', 'bestaudio',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--embed-thumbnail',
            '-o', output_template,
            '--external-downloader', 'aria2c',
            '--external-downloader-args', '-x 16 -s 16 -k 1M',
            url
        ]

    # Run the command
    try:
        print("Starting download... This might take a while.")
        subprocess.run(command, check=True)
        print(f"Download completed successfully and saved to {video_dir if format_type == 'mp4' else audio_dir}")
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
    print("[1] Best Quality Video (1080p)")
    print("[2] Good Quality Video (720p)")
    print("[3] Fine Quality Video (480p)")
    print("[4] Best Audio (MP3)")
    format_choice = input("Enter the number corresponding to the format (1, 2, 3, or 4): ").strip()

    if format_choice == '1':
        format_type = 'mp4'
        quality = 'best'
    elif format_choice == '2':
        format_type = 'mp4'
        quality = 'good'
    elif format_choice == '3':
        format_type = 'mp4'
        quality = 'fine'
    elif format_choice == '4':
        format_type = 'mp3'
        quality = 'best'
    else:
        print("Invalid choice! Please enter '1', '2', '3', or '4'.")
        sys.exit(1)

    # Call the download function
    download_video(url, format_type, quality)

if __name__ == '__main__':
    main()
