import cv2
import os
import sys

# Preluăm ID-ul angajatului din argumente
user_id = sys.argv[1]

if not os.path.exists("dataset"):
    os.makedirs("dataset")

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(0)

count = 0

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1
        face_img = gray[y:y + h, x:x + w]
        cv2.imwrite(f"dataset/{user_id}_{count}.jpg", face_img)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cv2.imshow("Captură față", frame)

    if count >= 20:
        break

cap.release()
cv2.destroyAllWindows()
print(f"✅ Captură completă pentru angajatul ID {user_id}.")
