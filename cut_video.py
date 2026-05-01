import os
import subprocess
import shutil
import winreg

SEGMENT_DURATION = 120  # 2 phút
OUTPUT_DIR = "output"


def refresh_path_from_registry():
    """Refresh PATH environment variable from Windows registry"""
    try:
        # Get system PATH
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as key:
            system_path = winreg.QueryValueEx(key, 'Path')[0]
        
        # Get user PATH
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r'Environment') as key:
            try:
                user_path = winreg.QueryValueEx(key, 'Path')[0]
            except:
                user_path = ""
        
        # Combine and update
        new_path = f"{user_path};{system_path}"
        os.environ['PATH'] = new_path
    except:
        pass


def check_ffmpeg():
    return shutil.which("ffmpeg") is not None


def install_ffmpeg():
    print("Đang cài FFmpeg...")

    try:
        subprocess.run(
            ["winget", "install", "-e", "--id", "Gyan.FFmpeg"],
            check=True
        )
        return True
    except:
        pass

    try:
        subprocess.run(
            ["choco", "install", "ffmpeg", "-y"],
            check=True
        )
        return True
    except:
        pass

    print("Không cài được FFmpeg tự động.")
    return False


def split_video(file):
    filename = os.path.splitext(file)[0]

    cmd = [
        "ffmpeg",
        "-i", file,
        "-c", "copy",
        "-map", "0",
        "-f", "segment",
        "-segment_time", str(SEGMENT_DURATION),
        "-reset_timestamps", "1",
        os.path.join(OUTPUT_DIR, f"{filename}_part_%03d.mp4")
    ]

    subprocess.run(cmd, check=True)


def main():
    refresh_path_from_registry()
    
    if not check_ffmpeg():
        if not install_ffmpeg():
            return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = [f for f in os.listdir() if f.endswith(".mp4")]

    if not files:
        print("Không có file mp4 nào.")
        return

    for f in files:
        print(f"Đang xử lý: {f}")
        split_video(f)

    print(f"Hoàn tất! File nằm trong thư mục '{OUTPUT_DIR}'")


if __name__ == "__main__":
    main()
