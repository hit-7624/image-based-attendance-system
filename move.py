import os
import shutil

#123456

# Mac-specific paths
SRC_FOLDER = "/Users/hit/Library/Containers/604791CE-3C14-4B68-AA52-1F0D293EE927/Data/Documents/STDStorage/526614095"
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
DESTINATION_FOLDER = os.path.join(DESKTOP_PATH, "project", "captured")

# Ensure source folder exists
if not os.path.exists(SRC_FOLDER):
    raise FileNotFoundError(f"❌ Source folder not found: {SRC_FOLDER}")

# Ensure destination folder exists
os.makedirs(DESTINATION_FOLDER, exist_ok=True)

# Image prefix - keeping the same as your original script
image_prefix = "IMAGE_"

# Move matching files
moved_count = 0
for filename in os.listdir(SRC_FOLDER):
    if filename.startswith(image_prefix):
        source_path = os.path.join(SRC_FOLDER, filename)
        destination_path = os.path.join(DESTINATION_FOLDER, filename)
        shutil.move(source_path, destination_path)
        print(f"Moved: {filename}")
        moved_count += 1

if moved_count > 0:
    print(f"✅ All {moved_count} matching files have been moved successfully.")
else:
    print("ℹ️ No matching files found to move.")