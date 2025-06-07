import os
import shutil
from dotenv import load_dotenv

# Load config from env file
load_dotenv()
123 
# Get paths and prefix from .env
source_dir = os.getenv("SRC_FOLDER")
target_dir = os.getenv("DEST_FOLDER")
file_prefix = os.getenv("IMAGE_PREFIX")

if not source_dir or not target_dir or not file_prefix:
    print("Error: Please set SRC_FOLDER, DEST_FOLDER, and IMAGE_PREFIX in your .env file.")
    exit()

print(f"Source folder: {source_dir}")
print(f"Destination folder: {target_dir}")

if not os.path.exists(source_dir):
    print(f"Source folder not found: {source_dir}")
    exit()

if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print(f"Created destination folder: {target_dir}")

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
    print(f"All {files_moved} files have been moved successfully.")
else:
    print("No matching files found to move.")