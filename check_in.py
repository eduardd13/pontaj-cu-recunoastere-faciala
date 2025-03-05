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

def already_checked_in(user_id):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM attendance
        WHERE user_id = ? AND time_out IS NULL
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def log_attendance(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (user_id, date, time_in)
        VALUES (?, ?, ?)
    """, (user_id, today, time_now))
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

            if already_checked_in(user_id):
                print(f"⚠️ {name} are deja o pontare activă!")
                cap.release()
                cv2.destroyAllWindows()
                exit()

            log_attendance(user_id)
            print(f"✅ {name} a fost pontat!")

            cap.release()
            cv2.destroyAllWindows()
            exit()
        else:
            cv2.putText(frame, "Necunoscut", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow('Check-In', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
