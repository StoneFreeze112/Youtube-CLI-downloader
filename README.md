Here’s an updated version of your README with new information about using `aria2c` and an enhanced user guide for new users:

# YouTube Downloader Script

This script allows you to easily download videos and audio from YouTube in various formats. It utilizes `yt-dlp`, a powerful command-line tool, to fetch the content, along with `aria2c` for enhanced download speed and stability.

## Features

- Download videos in MP4 format with options for quality:
  - Best Quality (1080p)
  - Good Quality (720p)
  - Fine Quality (480p)
- Download audio in MP3 format automatically at the best quality.
- Utilizes `aria2c` as an external downloader for faster downloads.
- User-friendly prompts for easy interaction.

## Prerequisites

Before running the script, ensure you have the following installed on your system:

1. **Python (version 3.6 or higher)**
   - Download and install from [python.org](https://www.python.org/downloads/).

2. **yt-dlp**
   - Open your command prompt or terminal and run:
     ```bash
     pip install yt-dlp
     ```

3. **FFmpeg**
   - This is required for audio and video processing. Install it based on your operating system:

### Linux Installation Instructions

#### **Debian/Ubuntu**
```bash
sudo apt update
sudo apt install ffmpeg
```

#### **Fedora**
```bash
sudo dnf install ffmpeg
```

#### **CentOS/RHEL**
1. Enable the EPEL repository:
   ```bash
   sudo yum install epel-release
   ```
2. Install FFmpeg:
   ```bash
   sudo yum install ffmpeg
   ```

#### **Arch Linux**
```bash
sudo pacman -S ffmpeg
```

#### **OpenSUSE**
```bash
sudo zypper install ffmpeg
```

#### **Linux Mint**
```bash
sudo apt update
sudo apt install ffmpeg
```

#### **Other Distributions**
- For other Linux distributions, consult the documentation specific to your distribution on how to install FFmpeg. Most package managers should have it available.

4. **aria2c**
   - Download and install `aria2c` based on your operating system:

### Windows Installation Instructions
- **Using Chocolatey** (if installed):
  ```bash
  choco install aria2
  ```
- **Manual Installation**:
  1. Download from the [aria2 releases page](https://github.com/aria2/aria2/releases).
  2. Extract and add the folder containing `aria2c.exe` to your system’s PATH.

### Linux Installation Instructions
```bash
sudo apt install aria2  # Debian/Ubuntu
sudo dnf install aria2  # Fedora
sudo yum install aria2  # CentOS/RHEL
```

## Running the Script

1. **Download the Script:**
   - Copy the script code into a text file and save it as `youtube_downloader.py`.

2. **Open Command Prompt or Terminal:**
   - **Windows:** Press `Win + R`, type `cmd`, and hit Enter.
   - **Linux/macOS:** Open your terminal application.

3. **Navigate to the Script Location:**
   Use the `cd` command to change directories to where you saved `youtube_downloader.py`. For example:
   ```bash
   cd path/to/your/script
   ```

4. **Run the Script:**
   Execute the script using:
   ```bash
   python youtube_downloader.py
   ```

5. **Follow the Prompts:**
   - Enter the YouTube link when prompted.
   - Choose the format by entering the corresponding number:
     - [1] Best Quality Video (1080p)
     - [2] Good Quality Video (720p)
     - [3] Fine Quality Video (480p)
     - [4] Best Audio (MP3)

The downloaded files will be saved in a folder named "YouTube Videos" in your Downloads directory. Audio files will be saved in a separate folder named "YouTube Music."

## Troubleshooting

- If the script exits with an error about missing dependencies, ensure that `yt-dlp`, `ffmpeg`, and `aria2c` are correctly installed and added to your PATH.
- If you encounter any issues, double-check the YouTube link format and ensure your internet connection is stable.
- Make sure to run the script in an environment that has permission to access the specified output directories.

## License

This script is open-source and free to use. Feel free to modify and share it as needed.

---

This updated README includes detailed installation instructions for `aria2c` and clarifies the functionality related to audio and video downloads. If you need any further adjustments or additions, let me know!
