import face_recognition
import datetime
import os
import numpy as np
import write_attendance
import pickle
import shutil

# Lecture timing 
class_timings = [
    ("08:00", "09:20"),
    ("09:30", "10:20"),
    ("10:30", "11:20"),
    ("11:30", "12:20"),
    ("02:00", "03:59") 
]


WEEKLY_SCHEDULE = {
    "Monday":    ["CN", "AFL", "IS", "IS", None],
    "Tuesday":   ["MIT", "IS", "CN", "AI", None],
    "Wednesday": ["AFL", "CN", "AI", "MIT", None],
    "Thursday":  ["AFL", "AI", "MIT", None, None],
    "Friday":    ["IS", "MIT", "AI", None, None],
    "Saturday":  ["AI", "IS", "AI", "MIT", None],
    "Sunday":    ["AI", "IS", "CN", "AFL", None]
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

for img_path in class_photos:
    try:
        classroom_img = face_recognition.load_image_file(img_path)
        detected_faces = face_recognition.face_locations(classroom_img)
        student_encodings = face_recognition.face_encodings(classroom_img, detected_faces)

        for student_face in student_encodings:
            matched_faces = face_recognition.compare_faces(face_data, student_face)
            similarity_scores = face_recognition.face_distance(face_data, student_face)
            closest_match = np.argmin(similarity_scores)
            if matched_faces[closest_match]:
                present_students.add(student_ids[closest_match])
        
        # Move processed image to marked folder
        img_file = os.path.basename(img_path)
        saved_path = os.path.join("marked", img_file)
        shutil.move(img_path, saved_path)
        print(f"Processed and moved: {img_file}")
    except Exception as error:
        print(f"Error processing {img_path}: {error}")

# Save attendance record
attendance_file = f"attendance_data/{ongoing_subject}.xlsx"

print("Marking attendance for:", present_students)
write_attendance.mark_attendance(attendance_file, present_students, curr_date)
print(f"Attendance saved to {attendance_file}")