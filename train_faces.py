import face_recognition
import os
import pickle

training_dir = "training_data/"
known_face_encodings = []
known_roll_numbers = []

print("Training Model ...")
for person_folder in os.listdir(training_dir):
    person_path = os.path.join(training_dir, person_folder)
    if os.path.isdir(person_path):
        for image_file in os.listdir(person_path):
            image_path = os.path.join(person_path, image_file)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_roll_numbers.append(person_folder)

# Save encodings
with open("encodings.pkl", "wb") as f:
    pickle.dump((known_face_encodings, known_roll_numbers), f)

print("Model Trained and Saved Successfully!")