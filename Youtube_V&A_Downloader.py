#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import shutil
import json
import platform
import tempfile
import glob
import zipfile
from urllib.request import urlopen, urlretrieve
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
            print("📦 yt-dlp not found. Installing via pip...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            import yt_dlp
            USE_MODULE = True
            print("✅ yt-dlp installed successfully.")


# ==========================================================
# Package manager detection (Linux)
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
# aria2
# ==========================================================
def get_aria2_path():
    if shutil.which("aria2c"):
        return shutil.which("aria2c")

    print("📦 aria2c not found. Attempting install...")
    if platform.system() == "Linux":
        pm = get_package_manager()
        if pm:
            subprocess.check_call(pm + ["aria2"])
            return shutil.which("aria2c")

    print("⚠️ aria2 unavailable. Continuing without it.")
    return None


# ==========================================================
# ffmpeg
# ==========================================================
def get_ffmpeg_path():
    if shutil.which("ffmpeg"):
        return shutil.which("ffmpeg")

    print("📦 ffmpeg not found. Attempting install...")
    if platform.system() == "Linux":
        pm = get_package_manager()
        if pm:
            subprocess.check_call(pm + ["ffmpeg"])
            return shutil.which("ffmpeg")

    print("❌ ffmpeg is required for audio extraction.")
    return None


# ==========================================================
# URL input (yt-dlp does validation)
# ==========================================================
def get_youtube_url():
    while True:
        url = input("🔗 Enter YouTube link (Ctrl+C to exit): ").strip()
        if url and ("youtube.com" in url or "youtu.be" in url):
            return url
        print("❌ Invalid YouTube URL.")


# ==========================================================
# Playlist detection
# ==========================================================
def is_playlist(url):
    parsed = urlparse(url)
    return "list" in parse_qs(parsed.query)


# ==========================================================
# Format selection
# ==========================================================
def choose_format(is_playlist_flag):
    print("\n🎥 Choose download type:")
    print("[1] Video 1080p (Best)")
    print("[2] Video 720p (Good)")
    print("[3] Video 480p (Fine)")
    print("[4] Audio MP3")

    while True:
        choice = input("🎯 Select (1–4): ").strip()
        if choice in {"1", "2", "3", "4"}:
            break

    if choice == "4":
        download_playlist = False
        if is_playlist_flag:
            print("[1] Single audio\n[2] Full playlist")
            download_playlist = input("Choose: ").strip() == "2"
        return "bestaudio", True, None, download_playlist

    resolution = {"1": "1080", "2": "720", "3": "480"}[choice]
    return f"bestvideo[height<={resolution}]+bestaudio/best", False, resolution, False


# ==========================================================
# Resume logging
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
# Download
# ==========================================================
def download_video(url, fmt, is_audio, resolution, playlist):
    video_dir = os.path.expanduser("~/Downloads/YouTube Videos")
    audio_dir = os.path.expanduser("~/Downloads/YouTube Music")
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    out_dir = audio_dir if is_audio else video_dir
    outtmpl = os.path.join(out_dir, "%(title)s.%(ext)s")

    ffmpeg = get_ffmpeg_path() if is_audio else None
    aria2 = get_aria2_path()

    try:
        if USE_MODULE:
            import yt_dlp
            opts = {
                "format": fmt,
                "outtmpl": outtmpl,
                "noplaylist": not playlist,
                "continuedl": True,
                "retries": 10,
                "quiet": False,
            }

            if aria2:
                opts["external_downloader"] = "aria2c"
                opts["external_downloader_args"] = ["-x4", "-k1M"]

            if is_audio:
                opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3"
                }]
                opts["ffmpeg_location"] = ffmpeg

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

        else:
            cmd = ["yt-dlp", "-f", fmt, "-o", outtmpl, "--continue", "--retries", "10"]
            if playlist:
                cmd.append("--yes-playlist")
            else:
                cmd.append("--no-playlist")

            if aria2:
                cmd += ["--external-downloader", "aria2c",
                        "--external-downloader-args", "-x4 -k1M"]

            if is_audio:
                cmd += ["--extract-audio", "--audio-format", "mp3",
                        "--ffmpeg-location", ffmpeg]

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
    print("\n🎬 YouTube Downloader (Smart Resume Edition)\n")

    resume = check_resume()
    if resume:
        download_video(
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
            download_video(url, fmt, is_audio, res, playlist)
        except KeyboardInterrupt:
            print("\n👋 Exiting.")
            sys.exit(0)


if __name__ == "__main__":
    main()
