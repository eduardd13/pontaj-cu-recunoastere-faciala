import cv2
import numpy as np
import os

# Inițializăm modelul LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Funcție pentru încărcarea fețelor și ID-urilor
def get_images_and_labels(data_path):
    face_samples = []
    ids = []

    for file in os.listdir(data_path):
        if file.endswith(".jpg"):
            img_path = os.path.join(data_path, file)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            id = int(file.split("_")[0])  # Extragem ID-ul angajatului din numele fișierului
            faces = face_cascade.detectMultiScale(img)

            for (x, y, w, h) in faces:
                face_samples.append(img[y:y+h, x:x+w])
                ids.append(id)

    return face_samples, ids

# Încărcăm datele din dataset
faces, ids = get_images_and_labels("dataset/")

# ✅ Verificăm dacă există date suficiente pentru antrenare
if len(faces) == 0 or len(ids) == 0:
    print("❌ Eroare: Nu există suficiente date pentru antrenare! Adaugă cel puțin un angajat cu imagini în dataset.")
    exit()

# ✅ Antrenăm modelul
recognizer.train(faces, np.array(ids))
recognizer.save("trained_model.yml")

print(f"✅ Model antrenat cu succes folosind {len(faces)} fețe.")
