import os
import sys
import re
import time
import subprocess
import shutil
import json
from urllib.parse import urlparse, parse_qs

LOG_PATH = os.path.expanduser("~/Downloads/yt_incomplete.log")

def get_youtube_url():
    while True:
        url = input("🔗 Enter YouTube link (or press Ctrl+C to exit): ").strip()
        if re.search(r'(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}', url):
            return url
        print("❌ Invalid URL. Use format like: https://youtube.com/watch?v=abc12345678")

def is_playlist(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    return 'list' in query

def choose_format(is_playlist_flag):
    print("\n🎥 Choose your download:")
    print("[1] 📹 Video - 1080p (Best Quality)")
    print("[2] 📹 Video - 720p (Good Quality)")
    print("[3] 📹 Video - 480p (Fine Quality)")
    print("[4] 🎵 Audio - MP3 (Best Quality)")

    while True:
        choice = input("🎯 Pick a number (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            break

    if choice in ['1', '2', '3']:
        resolutions = {'1': '1080', '2': '720', '3': '480'}
        resolution = resolutions[choice]
        format_type = f'bestvideo[height<={resolution}]+bestaudio/best'
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
        if choice == '2':
            download_playlist = True

    return format_type, is_audio, resolution, download_playlist


def get_video_info(url):
    """Fetch YouTube title safely via yt-dlp"""
    try:
        cmd = [sys.executable, "-m", "yt_dlp", "-j", "--no-warnings", url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout.splitlines()[0])
            return data.get("title", "Unknown Title")
    except Exception:
        pass
    return "Unknown Title"


def log_unfinished_download(url, title, resolution):
    data = {"url": url, "title": title, "resolution": resolution, "timestamp": time.ctime()}
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"📝 Logged unfinished download: {title}")


def check_previous_unfinished():
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            print("\n⚠️ Detected unfinished download:")
            print(f"🎬 Title: {data['title']}")
            print(f"🔗 URL: {data['url']}")
            print(f"📺 Resolution: {data['resolution'] or 'Audio Only'}")
            choice = input("🔁 Redownload this video? (y/n): ").strip().lower()
            if choice == "y":
                return data
        except Exception:
            pass
    return None


def remove_unfinished_log():
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)


def download_with_retry(command, url, title, resolution):
    retries = 5
    delay = 1
    for attempt in range(retries):
        print(f"⏳ Attempt {attempt + 1}/{retries}...")
        try:
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
                for line in proc.stdout:
                    print(line, end="")
                proc.wait()

                if proc.returncode == 0:
                    return True  # success
                raise subprocess.CalledProcessError(proc.returncode, command)
        except FileNotFoundError:
            print("❌ yt-dlp or aria2c not found. Please install them or ensure they’re in PATH.")
            sys.exit(1)
        except subprocess.CalledProcessError:
            print(f"\n❌ Failed. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
    print("❌ Failed after 5 tries.")
    log_unfinished_download(url, title, resolution)
    return False


def download_video(url, format_type, is_audio, resolution, download_playlist):
    print("\n🚀 Preparing to download...")
    video_dir = os.path.expanduser('~/Downloads/YouTube Videos')
    audio_dir = os.path.expanduser('~/Downloads/YouTube Music')
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    output_template = os.path.join(
        audio_dir if is_audio else video_dir,
        '%(playlist_title)s/%(title)s.%(ext)s' if is_audio and download_playlist else '%(title)s.%(ext)s'
    )

    title = get_video_info(url)

    command = [sys.executable, "-m", "yt_dlp", "-f", format_type, "--embed-thumbnail", "-o", output_template]

    if shutil.which("aria2c"):
        command += ["--external-downloader", "aria2c",
                    "--external-downloader-args",
                    "--split=4 --max-connection-per-server=4 --min-split-size=1M"]
    else:
        print("⚠️ aria2c not found. Using yt-dlp internal downloader.")

    if is_audio:
        command += ["--extract-audio", "--audio-format", "mp3"]
        if download_playlist:
            command.append("--yes-playlist")
        print("🎵 Downloading MP3(s)...")
    else:
        print(f"📹 Downloading video - {resolution}p...")

    command.append(url)

    success = download_with_retry(command, url, title, resolution)
    if success:
        print(f"\n✅ Done! Saved to: {output_template}")
        remove_unfinished_log()


def main():
    print("🎥 YouTube Downloader 🎵 (Smart Resume Edition)")

    previous = check_previous_unfinished()
    if previous:
        download_video(previous["url"], 
                       f'bestvideo[height<={previous["resolution"]}]+bestaudio' if previous["resolution"] else 'bestaudio',
                       previous["resolution"] is None,
                       previous["resolution"],
                       False)
        return

    while True:
        try:
            url = get_youtube_url()
            is_playlist_flag = is_playlist(url)
            format_type, is_audio, resolution, download_playlist = choose_format(is_playlist_flag)
            download_video(url, format_type, is_audio, resolution, download_playlist)
            print("\n" + "="*60)
            print("✅ Download Complete! Ready for the next link.")
            print("="*60 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Exiting YouTube Downloader. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n⚠️ Unexpected error: {e}. Restarting...")
            time.sleep(1)
            continue


if __name__ == "__main__":
    main()
