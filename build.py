import os
import sys
import subprocess
import shutil

def build():
    print("Building Nomoject...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # PyInstaller
    cmd = [
        "pyinstaller",
        "--name=Nomoject",
        "--windowed",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--add-data", "locales;locales",
        "nomoject.py"
    ]
    
    # Add icon, if exists
    if os.path.exists("icon.ico"):
        cmd.extend(["--icon=icon.ico"])
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild completed successfully!")
        print(f"Executable location: {os.path.join('dist', 'Nomoject.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"\nError during build: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build() 