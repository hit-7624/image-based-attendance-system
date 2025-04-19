import face_recognition
import datetime
import os
import numpy as np
import write_attendance
import pickle
import shutil

# Lecture times in 24hr format (start, end)
lectures = [
    ("00:00", "03:30"),
    ("01:30", "02:30"),
    ("20:30", "23:30"),
    ("21:00", "12:30"),
    ("01:00", "03:59")  # Extra slot for testing
]

# Timetable with subjects per day and slot
TIME_TABLE = {
    "Monday":    ["CN", "AFL", "IS", "IS", None],
    "Tuesday":   ["AFL", "IS", "CN", "AI", None],
    "Wednesday": ["AFL", "CN", "AI", "MIT", None],
    "Thursday":  ["AFL", "AI", "MIT", None, None],
    "Friday":    ["IS", "MIT", "AI", None, None],
    "Saturday":  ["AI", "IS", "Ai", "MIT", None],
    "Sunday":    ["AI", "IS", "CN", None, None]
}

# Load saved face encodings
print("Loading trained model ...")
with open("encodings.pkl", "rb") as f:
    known_face_encodings, known_roll_numbers = pickle.load(f)
print("Model Loaded Successfully!")

# Determine current time and subject
now = datetime.datetime.now()
current_time = now.strftime("%H:%M")
current_day = now.strftime("%A")
current_date = now.strftime("%d-%m-%Y")

subject = None
for i, (start, end) in enumerate(lectures):
    if start <= current_time <= end:
        subject = TIME_TABLE.get(current_day, [None]*5)[i]
        break

if not subject:
    print("No lecture at this time.")
    exit()

print(f"Current Subject: {subject} on {current_day} at {current_time}")

# Create necessary folders if they don't exist
if not os.path.exists("captured"):
    os.makedirs("captured")
if not os.path.exists("marked"):
    os.makedirs("marked")
if not os.path.exists("attendance_data"):
    os.makedirs("attendance_data")

# Face Recognition
attendance = set()

# Get all image files from the captured folder
image_extensions = ['.jpg', '.jpeg', '.png']
test_images = []
if os.path.exists("captured"):
    for filename in os.listdir("captured"):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            test_images.append(os.path.join("captured", filename))
else:
    print(f"Warning: 'captured' folder does not exist. Creating it now.")
    os.makedirs("captured")
    print(f"Please place images in the 'captured' folder for attendance.")
    exit()

if not test_images:
    print(f"No images found in 'captured' folder. Please add images for processing.")
    exit()

print(f"Processing {len(test_images)} images from 'captured' folder...")

for image_path in test_images:
    try:
        test_image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(test_image)
        face_encodings = face_recognition.face_encodings(test_image, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distance = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distance)
            if matches[best_match_index]:
                attendance.add(known_roll_numbers[best_match_index])
        
        # Move processed image to marked folder
        filename = os.path.basename(image_path)
        marked_path = os.path.join("marked", filename)
        shutil.move(image_path, marked_path)
        print(f"Processed and moved: {filename}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

# Save attendance
subject_file = f"attendance_data/{subject}.xlsx"
# Ensure the attendance_data directory exists
if not os.path.exists("attendance_data"):
    os.makedirs("attendance_data")

print("Marking attendance for:", attendance)
write_attendance.mark_attendance(subject_file, attendance, current_date)
print(f"Attendance saved to {subject_file}")