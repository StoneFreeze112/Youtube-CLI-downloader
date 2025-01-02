#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check if script is run with root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or using sudo."
  exit 1
fi

# Install dependencies if not present
if ! command -v yt-dlp &> /dev/null; then
    echo "Installing yt-dlp..."
    apt-get update && apt-get install -y yt-dlp
fi

if ! command -v ffmpeg &> /dev/null; then
    echo "Installing ffmpeg..."
    apt-get install -y ffmpeg
fi

if ! command -v aria2c &> /dev/null; then
    echo "Installing aria2..."
    apt-get install -y aria2
fi

# Ensure ytd.py exists in the current directory
if [ ! -f "ytd.py" ]; then
  echo "Error: ytd.py not found in the current directory."
  exit 1
fi

# Copy the Python script to /usr/local/bin and make it executable
echo "Installing ytd..."
cp ytd.py /usr/local/bin/ytd
chmod +x /usr/local/bin/ytd

echo "ytd has been installed successfully. Use it by typing 'ytd <YouTube URL>'."

