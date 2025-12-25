#!/usr/bin/env python3
import os
import sys
import re
import time
import json
import shutil
import subprocess
import platform
from datetime import datetime

# =========================
# ✈️ V-CORE BLACK BOX SETUP
# =========================

VCORE_LOG_DIR = os.path.expanduser("~/Downloads/VCORE_LOGS")
os.makedirs(VCORE_LOG_DIR, exist_ok=True)

def human_log(filename, title, what, why, tried, cannot_fix):
    path = os.path.join(VCORE_LOG_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")
        f.write("What happened:\n")
        f.write(what + "\n\n")
        f.write("Why this happened:\n")
        f.write(why + "\n\n")
        f.write("What V-Core tried:\n")
        f.write(tried + "\n\n")
        f.write("Why it could not fix it:\n")
        f.write(cannot_fix + "\n\n")
        f.write(f"Timestamp: {datetime.now()}\n")

# =========================
# 🧠 V-CORE CORES
# =========================

class FatherCore:
    """Defines what 'correct' means"""

    YT_REGEX = re.compile(r'(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}')

    @staticmethod
    def check_youtube_url(url):
        return bool(FatherCore.YT_REGEX.search(url))


class MotherCore:
    """Attempts fixes based on known playbooks"""

    @staticmethod
    def explain_invalid_url(url):
        return {
            "what": f"The input '{url}' is not a valid YouTube video link.",
            "why": (
                "YouTube video links must contain a video ID. "
                "Shorts links, empty input, or copied text often break this."
            ),
            "tried": (
                "V-Core checked the format of the link "
                "and waited for a correct one."
            ),
            "cannot_fix": (
                "V-Core cannot guess the correct video. "
                "A valid YouTube link must be provided by a human."
            )
        }

    @staticmethod
    def explain_missing_tool(tool):
        return {
            "what": f"The required tool '{tool}' is not installed.",
            "why": f"{tool} is required for downloading or processing media.",
            "tried": f"V-Core attempted to locate or install {tool}.",
            "cannot_fix": (
                "Automatic installation failed or is not supported "
                "on this system."
            )
        }


class ChristCore:
    """Validates actions and decides when to stop"""

    @staticmethod
    def approve_or_abort(condition, log_data, log_name, log_title):
        if not condition:
            human_log(
                filename=log_name,
                title=log_title,
                what=log_data["what"],
                why=log_data["why"],
                tried=log_data["tried"],
                cannot_fix=log_data["cannot_fix"]
            )
            print(f"\n🛑 V-CORE HALT — See log: {log_name}\n")
            return False
        return True

# =========================
# 🔧 SYSTEM CHECKS
# =========================

def ensure_yt_dlp():
    if shutil.which("yt-dlp"):
        return True
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        return True
    except Exception:
        return False

# =========================
# 🎥 USER INTERACTION
# =========================

def get_youtube_url():
    return input("🔗 Enter YouTube link: ").strip()

# =========================
# 🚀 MAIN FLOW
# =========================

def main():
    print("✈️ V-CORE AUTONOMOUS DOWNLOADER ACTIVE")

    # yt-dlp check
    yt_ok = ensure_yt_dlp()
    ChristCore.approve_or_abort(
        yt_ok,
        MotherCore.explain_missing_tool("yt-dlp"),
        "MISSING_DOWNLOADER_TOOL.txt",
        "Downloader Tool Missing"
    )

    while True:
        url = get_youtube_url()

        # EMPTY INPUT
        if not url:
            data = MotherCore.explain_invalid_url("empty input")
            ChristCore.approve_or_abort(
                False,
                data,
                "EMPTY_INPUT_PROVIDED.txt",
                "No Link Was Entered"
            )
            continue

        # URL VALIDATION
        valid = FatherCore.check_youtube_url(url)
        approved = ChristCore.approve_or_abort(
            valid,
            MotherCore.explain_invalid_url(url),
            "INVALID_YOUTUBE_LINK.txt",
            "Invalid YouTube Link Provided"
        )

        if not approved:
            continue

        # If valid, attempt download
        print("✅ Link looks valid. Attempting download...\n")

        try:
            subprocess.check_call(["yt-dlp", url])
            print("\n🎉 Download completed successfully.")
            break
        except Exception as e:
            human_log(
                "DOWNLOAD_FAILED.txt",
                "Download Failed",
                what=str(e),
                why="yt-dlp returned an error during download.",
                tried="V-Core executed yt-dlp with the provided link.",
                cannot_fix="The error occurred inside yt-dlp or the network."
            )
            print("\n❌ Download failed. See V-Core logs.")
            break

if __name__ == "__main__":
    main()
