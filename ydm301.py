#!/usr/bin/env python3
import os
import sys
import json
import shutil
import subprocess
import platform
from urllib.parse import urlparse, parse_qs

LOG_PATH = os.path.expanduser("~/Downloads/yt_incomplete.log")
USE_MODULE = False


# ==========================================================
# yt-dlp setup
# ==========================================================
def setup_yt_dlp():
    global USE_MODULE
    try:
        import yt_dlp
        USE_MODULE = True
        print("✅ Using yt-dlp Python module.")
    except ImportError:
        if shutil.which("yt-dlp"):
            USE_MODULE = False
            print("✅ Using system yt-dlp executable.")
        else:
            print("📦 Installing yt-dlp...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
            USE_MODULE = True


# ==========================================================
# Package manager detection
# ==========================================================
def get_package_manager():
    if shutil.which("apt"):
        return ["sudo", "apt", "install", "-y"]
    if shutil.which("dnf"):
        return ["sudo", "dnf", "install", "-y"]
    if shutil.which("pacman"):
        return ["sudo", "pacman", "-S", "--noconfirm"]
    return None


# ==========================================================
# ffmpeg
# ==========================================================
def ensure_ffmpeg():
    if shutil.which("ffmpeg"):
        return shutil.which("ffmpeg")

    print("📦 ffmpeg not found. Installing...")
    pm = get_package_manager()
    if pm:
        subprocess.check_call(pm + ["ffmpeg"])
        return shutil.which("ffmpeg")

    print("❌ ffmpeg is required.")
    sys.exit(1)


# ==========================================================
# aria2 (OPTIONAL, SAFE MODE)
# ==========================================================
def get_aria2():
    if shutil.which("aria2c"):
        return "aria2c"
    return None


# ==========================================================
# URL helpers
# ==========================================================
def is_playlist(url):
    parsed = urlparse(url)
    return "list" in parse_qs(parsed.query)


def get_youtube_url():
    while True:
        url = input("🔗 Enter YouTube link (Ctrl+C to exit): ").strip()
        if url and ("youtube.com" in url or "youtu.be" in url):
            return url
        print("❌ Invalid YouTube URL.")


# ==========================================================
# Format selection
# ==========================================================
def choose_format(has_playlist):
    print("\n🎥 Choose download type:")
    print("[1] Video 1080p (Best)")
    print("[2] Video 720p (Good)")
    print("[3] Video 480p (Fine)")
    print("[4] Audio MP3 (with thumbnail)")

    while True:
        c = input("🎯 Select (1–4): ").strip()
        if c in {"1", "2", "3", "4"}:
            break

    if c == "4":
        playlist = False
        if has_playlist:
            playlist = input("Download full playlist? (y/n): ").lower() == "y"
        return "bestaudio/best", True, None, playlist

    res = {"1": "1080", "2": "720", "3": "480"}[c]
    return f"bv*[height<={res}]+ba/b", False, res, False


# ==========================================================
# Resume handling
# ==========================================================
def log_unfinished(url, meta):
    with open(LOG_PATH, "w") as f:
        json.dump({"url": url, **meta}, f, indent=2)


def check_resume():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            data = json.load(f)
        print("\n⚠️ Resume previous download?")
        print(data["url"])
        if input("(y/n): ").lower() == "y":
            return data
    return None


def clear_resume():
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)


# ==========================================================
# Download logic (FIXED)
# ==========================================================
def download_media(url, fmt, is_audio, resolution, playlist):
    video_dir = os.path.expanduser("~/Downloads/YouTube Videos")
    audio_dir = os.path.expanduser("~/Downloads/YouTube Music")

    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    out_dir = audio_dir if is_audio else video_dir
    outtmpl = os.path.join(out_dir, "%(title)s.%(ext)s")

    ffmpeg = ensure_ffmpeg()
    aria2 = get_aria2()

    try:
        if USE_MODULE:
            import yt_dlp

            ydl_opts = {
                "format": fmt,
                "outtmpl": outtmpl,
                "noplaylist": not playlist,
                "continuedl": True,
                "retries": 10,
                "quiet": False,
                "ffmpeg_location": ffmpeg,
            }

            # SAFE aria2 usage (yt-dlp controls auth)
            if aria2:
                ydl_opts["downloader"] = "aria2c"
                ydl_opts["downloader_args"] = {
                    "aria2c": ["-x4", "-k1M"]
                }

            # 🔥 AUDIO FIX (THIS IS THE IMPORTANT PART)
            if is_audio:
                ydl_opts.update({
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "0",
                        },
                        {"key": "EmbedThumbnail"},
                        {"key": "FFmpegMetadata"},
                    ],
                    "writethumbnail": True,
                    "addmetadata": True,
                    "prefer_ffmpeg": True,
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        else:
            # CLI fallback (also FIXED)
            cmd = [
                "yt-dlp",
                "-f", fmt,
                "-o", outtmpl,
                "--continue",
                "--retries", "10",
                "--add-metadata",
                "--embed-thumbnail",
            ]

            if playlist:
                cmd.append("--yes-playlist")
            else:
                cmd.append("--no-playlist")

            if aria2:
                cmd += [
                    "--downloader", "aria2c",
                    "--downloader-args", "aria2c:-x4 -k1M"
                ]

            if is_audio:
                cmd += ["--extract-audio", "--audio-format", "mp3"]

            cmd.append(url)
            subprocess.check_call(cmd)

        clear_resume()
        print(f"\n✅ Download complete → {out_dir}")

    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        log_unfinished(url, {
            "format": fmt,
            "audio": is_audio,
            "resolution": resolution,
            "playlist": playlist
        })


# ==========================================================
# Main
# ==========================================================
def main():
    setup_yt_dlp()
    print("\n🎬 YouTube Downloader (MP3 Thumbnail FIXED Edition)\n")

    resume = check_resume()
    if resume:
        download_media(
            resume["url"],
            resume["format"],
            resume["audio"],
            resume.get("resolution"),
            resume.get("playlist", False)
        )
        return

    while True:
        try:
            url = get_youtube_url()
            fmt, is_audio, res, playlist = choose_format(is_playlist(url))
            download_media(url, fmt, is_audio, res, playlist)
        except KeyboardInterrupt:
            print("\n👋 Exiting.")
            sys.exit(0)


if __name__ == "__main__":
    main()
