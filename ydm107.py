import os
import subprocess
import sys
import re
import time
from urllib.parse import urlparse, parse_qs

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
    """Display format options and return download parameters."""
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
    else:
        format_type = 'bestaudio'
        is_audio = True
        resolution = None

    download_playlist = False
    if is_audio and is_playlist_flag:
        print("\nThis link is part of a playlist. Do you want to download:")
        print("[1] Only this audio")
        print("[2] The entire playlist")
        while True:
            choice = input("Enter 1 or 2: ").strip()
            if choice in ['1', '2']:
                break
            print("Please enter 1 or 2.")
        if choice == '2':
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
    """Handle the download process."""
    print("\n🚀 Preparing to download...")
    video_dir = os.path.expanduser('~/Downloads/YouTube Videos')
    audio_dir = os.path.expanduser('~/Downloads/YouTube Music')
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    output_template = os.path.join(
        audio_dir if is_audio else video_dir,
        '%(playlist_title)s/%(title)s.%(ext)s' if is_audio and download_playlist else '%(title)s.%(ext)s'
    )

    command = [
        'yt-dlp',
        '-f', format_type,
        '--embed-thumbnail',
        '-o', output_template,
        '--external-downloader', 'aria2c',
        '--external-downloader-args', '--split=4 --max-connection-per-server=4 --min-split-size=1M',
        url
    ]

    if is_audio:
        command.extend(['--extract-audio', '--audio-format', 'mp3'])
        if download_playlist:
            command.append('--yes-playlist')
        print("🎵 Downloading MP3(s)...")
    else:
        print(f"📹 Downloading video - {resolution}p...")

    download_with_retry(command)
    print(f"\n✅ Done! Saved to: {output_template}")

def main():
    print("🎥 YouTube Downloader 🎵 (No Checks)")
    url = get_youtube_url()
    is_playlist_flag = is_playlist(url)
    format_type, is_audio, resolution, download_playlist = choose_format(is_playlist_flag)
    download_video(url, format_type, is_audio, resolution, download_playlist)

if __name__ == '__main__':
    main()
