import os
import shutil
import getpass
import platform
from dotenv import load_dotenv

# Load config from env file
load_dotenv()

# Get current user info
username = getpass.getuser().lower()
system = platform.system()  # Gets Windows, Darwin, or Linux

print(f"Detected user: {username} on {system}")

# Set paths based on user's system
if username == "hit" or system == "Darwin":  # Mac user settings
    # Use Mac paths from config
    source_dir = os.getenv("MAC_SRC_FOLDER")
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    target_dir = os.path.join(desktop, "project", "captured")
    file_prefix = os.getenv("MAC_IMAGE_PREFIX")
else: 
    #windows
    desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    source_dir = desktop
    target_dir = os.getenv("WIN_DEST_FOLDER")
    file_prefix = os.getenv("WIN_IMAGE_PREFIX")

print(f"Source folder: {source_dir}")
print(f"Destination folder: {target_dir}")

# Make sure source exists
if not os.path.exists(source_dir):
    raise FileNotFoundError(f"Source folder not found: {source_dir}")

# move files
files_moved = 0
print(f"Moving files starting with: '{file_prefix}'")

for file in os.listdir(source_dir):
    if file.startswith(file_prefix):
        src_path = os.path.join(source_dir, file)
        dst_path = os.path.join(target_dir, file)
        
        shutil.move(src_path, dst_path)
        print(f"Moved: {file}")
        files_moved += 1

# Show summary
if files_moved > 0:
    print(f"All {files_moved} matching files have been moved successfully.")
else:
    print("No matching files found to move.")