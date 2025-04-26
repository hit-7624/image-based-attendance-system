import face_recognition
import datetime
import os
import numpy as np
import write_attendance
import pickle
import shutil
from PIL import Image, ImageDraw, ImageFont
import time

# Lecture timing 
class_timings = [
    ("00:01", "02:50"),
    ("09:30", "10:20"),
    ("10:30", "11:20"),
    ("11:30", "14:20"),
    ("20:00", "23:59") 
]


WEEKLY_SCHEDULE = {
    "Monday":    ["CN", "AFL", "IS", "IS", "MITLAB"],
    "Tuesday":   ["MIT", "IS", "CN", "AI", "AILAB"],
    "Wednesday": ["AFL", "CN", "AI", "MIT", "CNLAB"],
    "Thursday":  ["AFL", "AI", "MIT", None, "ISLAB"],
    "Friday":    ["IS", "MIT", "AI", "AILAB", "AILAB"],
    "Saturday":  ["AILAB", None, None, None, None]
}

# Load saved face encodings
print("Loading trained model ...")
with open("encodings.pkl", "rb") as model_file:
    face_data, student_ids = pickle.load(model_file)
print("Model Loaded Successfully!")

# Get current time and class
today = datetime.datetime.now()
curr_time = today.strftime("%H:%M")
curr_day = today.strftime("%A")
curr_date = today.strftime("%d-%m-%Y")

ongoing_subject = None
for slot_index, (start_time, end_time) in enumerate(class_timings):
    if start_time <= curr_time <= end_time:
        ongoing_subject = WEEKLY_SCHEDULE.get(curr_day, [None]*5)[slot_index]
        break

if not ongoing_subject:
    print("No lecture is scheduled at this time.")
    exit()

print(f"Current Subject: {ongoing_subject} on {curr_day} at {curr_time}")

# Create necessary directories if they don't exist
marked_subject_dir = os.path.join("marked", ongoing_subject)
processed_raw_dir = "processed_raw"
os.makedirs(marked_subject_dir, exist_ok=True)
os.makedirs(processed_raw_dir, exist_ok=True)


present_students = set()


formats = ['.jpg', '.jpeg', '.png']
class_photos = []

for img_name in os.listdir("captured"):
    if any(img_name.lower().endswith(ext) for ext in formats):
        class_photos.append(os.path.join("captured", img_name))


if not class_photos:
    print(f"No images found in 'captured' folder. Please add images for processing.")
    exit()

print(f"Processing {len(class_photos)} images from 'captured' folder...")

# Load a font for drawing text (optional, default font can be used)
try:
    font = ImageFont.truetype("arial.ttf", 30) 
except IOError:
    font = ImageFont.load_default()
    print("Arial font not found. Using default font.")


# Counter for unique filenames on the same date
file_counter = 0 

for img_path in class_photos:
    try:
        print(f"Processing {os.path.basename(img_path)}...")
        # Load image for face_recognition (numpy array)
        fr_image = face_recognition.load_image_file(img_path)
        # Load image with Pillow for drawing
        pil_image = Image.open(img_path).convert("RGB") # Convert to RGB for drawing
        draw = ImageDraw.Draw(pil_image)

        # Find faces
        detected_faces = face_recognition.face_locations(fr_image)
        student_encodings = face_recognition.face_encodings(fr_image, detected_faces)

        # Process each face found in the image
        for face_encoding, face_location in zip(student_encodings, detected_faces):
            matched_faces = face_recognition.compare_faces(face_data, face_encoding)
            similarity_scores = face_recognition.face_distance(face_data, face_encoding)
            closest_match_index = np.argmin(similarity_scores)

            name = "Unknown" # Default name
            # Check similarity threshold (0.6 is a common starting point, adjust as needed)
            if matched_faces[closest_match_index] and similarity_scores[closest_match_index] < 0.6: 
                student_id = student_ids[closest_match_index]
                present_students.add(student_id)
                name = student_id # Use student ID as name

                # Draw bounding box and name
                top, right, bottom, left = face_location
                draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0), width=4) 
                # Get text size using textbbox for Pillow 10+ compatibility
                try:
                     text_bbox = draw.textbbox((0, 0), name, font=font)
                     text_width = text_bbox[2] - text_bbox[0]
                     text_height = text_bbox[3] - text_bbox[1]
                except AttributeError: # Fallback for older Pillow versions
                     text_width, text_height = draw.textsize(name, font=font)

                # Adjust text background rectangle for larger font
                draw.rectangle(((left, bottom - text_height - 10), (left + text_width + 8, bottom)), fill=(0, 255, 0), outline=(0, 255, 0))
                draw.text((left + 6, bottom - text_height - 7), name, fill=(0, 0, 0), font=font) # Black text


        # --- Save the annotated image ---
        file_counter += 1
        original_filename = os.path.basename(img_path)
        file_ext = os.path.splitext(original_filename)[1]
        # Use date and counter for unique name
        annotated_img_name = f"{curr_date}_{file_counter}{file_ext}" 
        annotated_img_path = os.path.join(marked_subject_dir, annotated_img_name)
        pil_image.save(annotated_img_path)
        print(f"Saved annotated image to: {annotated_img_path}")

        # --- Move the original image to processed_raw ---
        processed_raw_path = os.path.join(processed_raw_dir, original_filename)
        shutil.move(img_path, processed_raw_path)
        print(f"Moved original image to: {processed_raw_path}")

        # --- Clean up drawing object ---
        del draw 

    except Exception as error:
        print(f"Error processing {img_path}: {error}")
        # Optionally move errored images to a separate folder
        error_dir = "errored_images"
        os.makedirs(error_dir, exist_ok=True)
        try:
            shutil.move(img_path, os.path.join(error_dir, os.path.basename(img_path)))
            print(f"Moved errored image {os.path.basename(img_path)} to {error_dir}")
        except Exception as move_error:
            print(f"Could not move errored image {os.path.basename(img_path)}: {move_error}")


# Save attendance record
attendance_file = f"attendance_data/{ongoing_subject}.xlsx"

print("Marking attendance for:", present_students)
write_attendance.mark_attendance(attendance_file, present_students, curr_date)
print(f"Attendance saved to {attendance_file}")