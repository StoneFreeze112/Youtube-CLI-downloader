import os
import subprocess
import sys
import re

def check_dependencies():
    """Check if required dependencies are installed and install missing ones."""
    print("Checking for dependencies...")
    dependencies = ['yt-dlp', 'ffmpeg', 'aria2c']
    missing = []

    for dep in dependencies:
        command = 'where' if os.name == 'nt' else 'which'
        if subprocess.call([command, dep], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) != 0:
            missing.append(dep)

    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        choice = input("Do you want to install the missing dependencies automatically? (y/n): ").strip().lower()
        if choice == 'y':
            install_dependencies(missing)
        else:
            print("Please install the missing dependencies and try again.")
            sys.exit(1)
    else:
        print("All dependencies are installed.")

def install_dependencies(missing):
    """Install missing dependencies based on the OS and package manager."""
    try:
        if os.name == 'nt':
            for dep in missing:
                subprocess.check_call(["choco", "install", dep, "-y"])
        else:
            distro = get_linux_distro()
            package_manager, install_cmd = get_package_manager(distro)
            
            for dep in missing:
                print(f"Installing {dep} using {package_manager}...")
                subprocess.check_call(install_cmd + [dep])
        print("Dependencies installed successfully. Please restart the script.")
    except Exception as e:
        print(f"Error installing dependencies: {str(e)}")
        sys.exit(1)

def get_linux_distro():
    """Detect the Linux distribution."""
    try:
        with open('/etc/os-release') as f:
            for line in f:
                if line.startswith('ID='):
                    return line.split('=')[1].strip().strip('"')
    except FileNotFoundError:
        print("Unable to detect Linux distribution. Defaulting to Debian-based.")
        return "debian"

def get_package_manager(distro):
    """Return the package manager and install command based on the Linux distro."""
    package_managers = {
        "debian": ("APT", ["sudo", "apt-get", "install", "-y"]),
        "ubuntu": ("APT", ["sudo", "apt-get", "install", "-y"]),
        "arch": ("Pacman", ["sudo", "pacman", "-S", "--noconfirm"]),
        "manjaro": ("Pacman", ["sudo", "pacman", "-S", "--noconfirm"]),
        "fedora": ("DNF", ["sudo", "dnf", "install", "-y"]),
        "centos": ("YUM", ["sudo", "yum", "install", "-y"]),
        "opensuse": ("Zypper", ["sudo", "zypper", "install", "-y"])
    }
    return package_managers.get(distro, ("APT", ["sudo", "apt-get", "install", "-y"]))

def get_youtube_url():
    """Get and validate the YouTube URL from the user."""
    url = input("Enter the YouTube link (or 'e' to exit): ").strip()
    if url.lower() == 'e':
        print("Exiting the program.")
        sys.exit(0)
    if not re.match(r'(https?://)?(www\.)?(youtube|youtu\.be)', url):
        print("Invalid URL. Please provide a valid YouTube link.")
        return get_youtube_url()
    return url

def choose_format():
    """Let the user choose the download format."""
    print("Choose the format:")
    print("[1] Best Quality Video (1080p)")
    print("[2] Good Quality Video (720p)")
    print("[3] Fine Quality Video (480p)")
    print("[4] Best Audio (MP3)")

    choice = input("Enter the number corresponding to the format (1, 2, 3, or 4): ").strip()

    format_dict = {
        '1': 'bestvideo[height<=1080]+bestaudio',
        '2': 'bestvideo[height<=720]+bestaudio',
        '3': 'bestvideo[height<=480]+bestaudio',
        '4': 'mp3'
    }

    if choice in format_dict:
        return format_dict[choice], choice == '4'
    else:
        print("Invalid choice! Please enter '1', '2', '3', or '4'.")
        return choose_format()

def download_video(url, format_type, is_audio, retries=3):
    """Download the video or audio using yt-dlp and aria2c."""
    print("Preparing to download...")

    # Define output directories
    video_dir = os.path.expanduser('~/Downloads/YouTube Videos')
    audio_dir = os.path.expanduser('~/Downloads/YouTube Music')
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    if is_audio:
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
    else:
        output_template = os.path.join(video_dir, '%(title)s.%(ext)s')
        command = [
            'yt-dlp',
            '-f', format_type,
            '--embed-thumbnail',
            '-o', output_template,
            '--external-downloader', 'aria2c',
            '--external-downloader-args', '-x 16 -s 16 -k 1M',
            url
        ]

    for attempt in range(retries):
        print(f"Download attempt {attempt + 1}...")
        try:
            subprocess.run(command, check=True)
            print(f"Download completed successfully. Saved to: {output_template}")

            # Clear the terminal window after download
            clear_command = 'cls' if os.name == 'nt' else 'clear'
            subprocess.call(clear_command, shell=True)
            return
        except subprocess.CalledProcessError as e:
            print(f"Download error: {str(e)}")
            if attempt == retries - 1:
                print("Download failed after all attempts.")
                sys.exit(1)

def main():
    """Main function to orchestrate the download."""
    check_dependencies()
    while True:
        url = get_youtube_url()
        format_type, is_audio = choose_format()
        download_video(url, format_type, is_audio)

if __name__ == '__main__':
    main()