import cv2
import sqlite3
import os
from datetime import datetime

# Verificăm existența modelului
if not os.path.exists("trained_model.yml"):
    print("❌ Modelul lipsește! Adaugă angajați și reantrenează.")
    exit()

# Încarcă modelul și clasificatorul
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trained_model.yml")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Obținem numele angajatului după ID
def get_employee_name(user_id):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nume FROM employees WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Necunoscut"

# Verificăm dacă există pontare activă
def get_open_attendance_id(user_id):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM attendance
        WHERE user_id = ? AND time_out IS NULL
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Înregistrăm depontarea
def log_checkout(attendance_id):
    time_now = datetime.now().strftime("%H:%M:%S")
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE attendance
        SET time_out = ?
        WHERE id = ?
    """, (time_now, attendance_id))
    conn.commit()
    conn.close()

# Pornim camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Eroare la deschiderea camerei.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Nu pot citi de la cameră.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        cv2.putText(frame, "Asteptam fata...", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

    for (x, y, w, h) in faces:
        user_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        if confidence < 60:
            name = get_employee_name(user_id)
            attendance_id = get_open_attendance_id(user_id)

            if not attendance_id:
                print(f"⚠️ {name} nu are o pontare activă pentru depontare!")
                cv2.putText(frame, f"{name} nu are pontare activa!", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
                cv2.imshow('Check-Out', frame)
                cv2.waitKey(3000)
                cap.release()
                cv2.destroyAllWindows()
                exit()

            log_checkout(attendance_id)
            print(f"✅ {name} a fost depontat!")
            cv2.putText(frame, f"{name} depontat!", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.imshow('Check-Out', frame)
            cv2.waitKey(3000)
            cap.release()
            cv2.destroyAllWindows()
            exit()
        else:
            cv2.putText(frame, "Necunoscut", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cv2.imshow('Check-Out - Apasă Q pentru a opri', frame)

    # ✅ Permitem oprirea cu tasta Q în orice moment
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("⏹️ De-pontarea a fost anulată de utilizator.")
        break

# Închidem camera și fereastra
cap.release()
cv2.destroyAllWindows()
