import os
import subprocess
import sys

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
    subprocess.run(command)

def main():
    # Get the YouTube link from the user
    url = input("Enter the YouTube link: ")
    
    # Ask for format (mp4 or mp3)
    format_type = input("Do you want to download as MP4 or MP3? (Enter 'mp4' or 'mp3'): ").strip().lower()
    if format_type not in ['mp4', 'mp3']:
        print("Invalid format type! Please enter 'mp4' or 'mp3'.")
        sys.exit(1)

    # Ask for resolution or quality
    if format_type == 'mp4':
        resolution = input("Enter the desired resolution (e.g., 720, 1080): ")
    else:
        resolution = input("Enter the desired audio quality (e.g., 128K, 192K): ")

    # Call the download function
    download_video(url, format_type, resolution)

if __name__ == '__main__':
    main()

