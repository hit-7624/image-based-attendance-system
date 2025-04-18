import face_recognition
import datetime
import os
import numpy as np
import write_attendance
import pickle

# Lecture times in 24hr format (start, end)
lectures = [
    ("00:00", "03:30"),
    ("01:30", "02:30"),
    ("21:30", "23:30"),
    ("11:30", "12:30"),
    ("21:00", "23:59")  # Extra slot for testing
]

# Timetable with subjects per day and slot
TIME_TABLE = {
    "Monday":    ["CN", "AFL", "IS", "IS", None],
    "Tuesday":   ["AFL", "IS", "CN", "AI", None],
    "Wednesday": ["AFL", "CN", "AI", "MIT", None],
    "Thursday":  ["AFL", "AI", "MIT", None, None],
    "Friday":    ["IS", "MIT", "CN", None, None],
    "Saturday":  ["AI", "IS", "CN", None, None],
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

# Face Recognition
attendance = set()
test_images = ["test_image1.jpeg"]
for image_path in test_images:
    test_image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(test_image)
    face_encodings = face_recognition.face_encodings(test_image, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distance = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distance)
        if matches[best_match_index]:
            attendance.add(known_roll_numbers[best_match_index])

# Save attendance
# subject_file = f"{subject}.xlsx"
subject_file  = f"attendance/{subject}.xlsx"
# print("Attendance file:", subject_file)
# print(os.path.abspath(subject_file))
if not os.path.exists("attendance"):
    os.makedirs("attendance")

print("Marking attendance for:", attendance)
write_attendance.mark_attendance(subject_file, attendance, current_date)
print(f"Attendance saved to {subject_file}")