import os
import subprocess
import sys
import re
import time
import requests
from urllib.parse import urlparse, parse_qs

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    dependencies = ['yt-dlp', 'ffmpeg', 'aria2c']
    missing = []
    for dep in dependencies:
        command = 'where' if os.name == 'nt' else 'which'
        if subprocess.call([command, dep], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) != 0:
            missing.append(dep)
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}. Install them first.")
        sys.exit(1)
    print("✅ All dependencies found.")

def check_internet():
    """Verify internet connectivity."""
    print("🌐 Checking internet...")
    try:
        requests.get("https://www.google.com", timeout=5)
        print("✅ Connected!")
    except requests.ConnectionError:
        print("❌ No internet. Please connect and retry.")
        sys.exit(1)

def get_youtube_url():
    """Get and validate YouTube URL from user."""
    while True:
        url = input("🔗 Enter YouTube link: ").strip()
        if re.search(r'(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}', url):
            return url
        print("❌ Invalid URL. Use format like: https://youtube.com/watch?v=abc12345678")

def is_playlist(url):
    """Check if the URL is a playlist by looking for 'list=' in the query parameters."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    return 'list' in query

def choose_format(is_playlist_flag):
    """Display format options and return download parameters, including playlist choice if applicable."""
    print("\n🎥 Choose your download:")
    print("[1] 📹 Video - 1080p (Best Quality)")
    print("[2] 📹 Video - 720p (Good Quality)")
    print("[3] 📹 Video - 480p (Fine Quality)")
    print("[4] 🎵 Audio - MP3 (Best Quality)")
    
    while True:
        choice = input("🎯 Pick a number (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            break
        print("❌ Please enter 1, 2, 3, or 4.")
    
    if choice in ['1', '2', '3']:
        resolutions = {'1': '1080', '2': '720', '3': '480'}
        resolution = resolutions[choice]
        format_type = f'bestvideo[height<={resolution}]+bestaudio'
        is_audio = False
    elif choice == '4':
        format_type = 'bestaudio'
        is_audio = True
        resolution = None
    
    download_playlist = False
    if choice == '4' and is_playlist_flag:
        print("\nThis link is part of a playlist. Do you want to download:")
        print("[1] Only this audio")
        print("[2] The entire playlist")
        while True:
            playlist_choice = input("Enter 1 or 2: ").strip()
            if playlist_choice in ['1', '2']:
                break
            print("Please enter 1 or 2.")
        if playlist_choice == '2':
            download_playlist = True
    
    return format_type, is_audio, resolution, download_playlist

def download_with_retry(command):
    """Download with retries on failure."""
    retries = 5
    delay = 1
    for attempt in range(retries):
        print(f"⏳ Attempt {attempt + 1}/{retries}...")
        try:
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
                for line in proc.stdout:
                    print(line, end='')
                proc.wait()
                if proc.returncode == 0:
                    return
                raise subprocess.CalledProcessError(proc.returncode, command)
        except subprocess.CalledProcessError:
            print(f"\n❌ Failed. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
    print(f"❌ Failed after {retries} tries.")
    sys.exit(1)

def download_video(url, format_type, is_audio, resolution, download_playlist):
    """Handle the download process, including playlist handling for audio."""
    print("\n🚀 Preparing to download...")
    video_dir = os.path.expanduser('~/Downloads/YouTube Videos')
    audio_dir = os.path.expanduser('~/Downloads/YouTube Music')
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    
    if is_audio:
        if download_playlist:
            # Save playlist audios in a folder named after the playlist
            output_template = os.path.join(audio_dir, '%(playlist_title)s', '%(title)s.%(ext)s')
        else:
            # Save single audio directly in YouTube Music
            output_template = os.path.join(audio_dir, '%(title)s.%(ext)s')
    else:
        # Save video directly in YouTube Videos
        output_template = os.path.join(video_dir, '%(title)s.%(ext)s')
    
    external_downloader_args = '--split=4 --max-connection-per-server=4 --min-split-size=1M'
    
    command = [
        'yt-dlp',
        '-f', format_type,
        '--embed-thumbnail',
        '-o', output_template,
        '--external-downloader', 'aria2c',
        '--external-downloader-args', external_downloader_args,
        url
    ]
    
    if is_audio and download_playlist:
        command.append('--yes-playlist')
    
    if is_audio:
        command.extend(['--extract-audio', '--audio-format', 'mp3'])
    
    if is_audio:
        if download_playlist:
            print("🎵 Downloading entire playlist as MP3...")
        else:
            print("🎵 Downloading single audio as MP3...")
    else:
        print(f"📹 Downloading video - {resolution}p...")

    download_with_retry(command)
    print(f"\n✅ Done! Saved to: {output_template}")

def main():
    print("🎥 YouTube Downloader 🎵")
    check_dependencies()
    check_internet()
    url = get_youtube_url()
    is_playlist_flag = is_playlist(url)
    format_type, is_audio, resolution, download_playlist = choose_format(is_playlist_flag)
    download_video(url, format_type, is_audio, resolution, download_playlist)

if __name__ == '__main__':
    main()
