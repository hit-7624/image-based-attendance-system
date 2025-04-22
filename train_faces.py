import face_recognition
import os
import pickle

student_photos_dir = "training_data/"
face_data = []
student_ids = []

print("Training Model ...")
for student_folder in os.listdir(student_photos_dir):
    student_path = os.path.join(student_photos_dir, student_folder)
    if os.path.isdir(student_path):
        for photo_file in os.listdir(student_path):
            photo_path = os.path.join(student_path, photo_file)
            student_image = face_recognition.load_image_file(photo_path)
            face_features = face_recognition.face_encodings(student_image)
            if face_features:
                face_data.append(face_features[0])
                student_ids.append(student_folder)

# Save encodings
with open("encodings.pkl", "wb") as model_file:
    pickle.dump((face_data, student_ids), model_file)

print("Model Trained and Saved Successfully!")