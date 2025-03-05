import cv2
import sqlite3
from datetime import datetime



# Incarcam modelul antrenat
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trained_model.yml")

# Initializam detectorul de fete
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Functie pentru a verifica si actualiza pontajul
def log_attendance(user_id):
    conn = sqlite3.connect("../attendance.db")
    cursor = conn.cursor()

    # Luam data curenta
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M%S")

    # Verificam daca exista deja o pontare azi pentru acest user
    cursor.execute("SELECT * FROM attendance WHERE user_id = ? AND Date = ?", (user_id, today))
    record = cursor.fetchone()

    if record is None:
        # Daca NU exista pontare azi, adaugam ora de intrare
        cursor.execute("INSERT INTO attendance (user_id, date, time_in) VALUES (?, ?, ?)", (user_id, today, current_time))
        print(f"Angajat {user_id} a fost pontat cu intrare la {current_time}")
    elif record [4] is None:
        # Daca exista pontaj azi DAR fara iesire, adaugam ora de iesire
        cursor.execute("UPDATE attendance SET time_out = ? WHERE user_id = ? AND date = ?", (current_time, user_id, today))
        print(f"Angajat {user_id} a fost de-pontat cu iesire la {current_time}")
    else:
        # Daca exista si intrare si iesire azi, nu mai facem nimic
        print (f"Angajatul {user_id} este deja pontat complet azi.")


    conn.commit()
    conn.close()

# Pornim camera web
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = gray [y:y+h, x:x+h]
        face_resized = cv2.resize(face, (200,200)) #asiguram aceeasi dimensiunea ca la antrenare
        id, confidence = recognizer.predict(face_resized)

        if confidence < 80: # Pragul de incredere (cu cat mai mic, cu atat mai sigur)
            log_attendance(id)
            cv2.putText(frame, f"ID: {id} ({round(confidence, 2)})", (x,y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 225, 0), 2)
        else:
            cv2.putText(frame, "Necunoscut", (x,y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0, 255), 2)

        cv2.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow("Pontaj automat", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()