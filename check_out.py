import cv2
import sqlite3
import os
from datetime import datetime

if not os.path.exists("trained_model.yml"):
    print("❌ Modelul lipsește! Adaugă angajați și reantrenează.")
    exit()

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trained_model.yml")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def get_employee_name(user_id):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nume FROM employees WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Necunoscut"

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

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        user_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        if confidence < 60:
            name = get_employee_name(user_id)

            attendance_id = get_open_attendance_id(user_id)
            if not attendance_id:
                print(f"⚠️ {name} nu are o pontare activă pentru depontare!")
                cap.release()
                cv2.destroyAllWindows()
                exit()

            log_checkout(attendance_id)
            print(f"✅ {name} a fost depontat!")

            cap.release()
            cv2.destroyAllWindows()
            exit()

cap.release()
cv2.destroyAllWindows()
