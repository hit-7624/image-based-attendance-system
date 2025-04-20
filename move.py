import os
import shutil
import getpass
import platform
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

#testing 12334

# Detect current user and system
current_username = getpass.getuser().lower()
current_system = platform.system()  # 'Windows', 'Darwin' (Mac), or 'Linux'

print(f"Detected user: {current_username} on {current_system}")

# Configure paths based on user and system using .env variables
if current_username == "hit" or current_system == "Darwin":  # For user "hit" or any Mac user
    # Get Mac configuration from environment variables
    SRC_FOLDER = os.getenv("MAC_SRC_FOLDER")
    DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
    DESTINATION_FOLDER = os.path.join(DESKTOP_PATH, "project", "captured")
    image_prefix = os.getenv("MAC_IMAGE_PREFIX")
else:  # For Windows user
    # Get Windows configuration from environment variables
    win_src = os.getenv("WIN_SRC_FOLDER")
    
    # Handle different Desktop locations on Windows
    if win_src == "OneDrive\\Desktop":
        DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        if not os.path.exists(DESKTOP_PATH):
            DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        DESKTOP_PATH = os.path.join(os.path.expanduser("~"), win_src)
    
    SRC_FOLDER = DESKTOP_PATH
    DESTINATION_FOLDER = os.getenv("WIN_DEST_FOLDER")
    image_prefix = os.getenv("WIN_IMAGE_PREFIX")

print(f"Source folder: {SRC_FOLDER}")
print(f"Destination folder: {DESTINATION_FOLDER}")

# Ensure source folder exists
if not os.path.exists(SRC_FOLDER):
    # Try alternate path if default not found (for Windows)
    if current_system == "Windows":
        alt_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(alt_desktop) and SRC_FOLDER != alt_desktop:
            print(f"Primary source folder not found, trying: {alt_desktop}")
            SRC_FOLDER = alt_desktop
        else:
            alt_onedrive = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
            if os.path.exists(alt_onedrive) and SRC_FOLDER != alt_onedrive:
                print(f"Primary source folder not found, trying: {alt_onedrive}")
                SRC_FOLDER = alt_onedrive
    
    # If still doesn't exist, raise error
    if not os.path.exists(SRC_FOLDER):
        raise FileNotFoundError(f"❌ Source folder not found: {SRC_FOLDER}")

# Ensure destination folder exists
os.makedirs(DESTINATION_FOLDER, exist_ok=True)

# Move matching files
moved_count = 0
print(f"Looking for files starting with: '{image_prefix}'")

for filename in os.listdir(SRC_FOLDER):
    if filename.startswith(image_prefix):
        source_path = os.path.join(SRC_FOLDER, filename)
        destination_path = os.path.join(DESTINATION_FOLDER, filename)
        
        try:
            shutil.move(source_path, destination_path)
            print(f"Moved: {filename}")
            moved_count += 1
        except Exception as e:
            print(f"Error moving {filename}: {str(e)}")

# Final status message
if moved_count > 0:
    print(f"✅ All {moved_count} matching files have been moved successfully.")
else:
    print("ℹ️ No matching files found to move.")