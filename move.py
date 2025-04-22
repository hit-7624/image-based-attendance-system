import os
import shutil
import getpass
import platform
from dotenv import load_dotenv

# Load config from env file
load_dotenv()

#which user 
username = getpass.getuser().lower()
system = platform.system() 

print(f"Detected user: {username} on {system}")

#check for windows or mac
if username == "hit" or system == "Darwin":  # Mac user settings
    #mac
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

#giev error if there is no folder
if not os.path.exists(source_dir):
    print(f"Source folder not found: {source_dir}")
    exit() 

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


if files_moved > 0:
    print(f"All {files_moved}  files have been moved successfully.")
else:
    print("No matching files found to move.")