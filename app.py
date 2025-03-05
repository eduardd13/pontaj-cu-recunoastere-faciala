import sys
import subprocess
import os
import sqlite3
import csv
import openpyxl
from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    message = request.args.get('message', '')
    model_status = ""
    if not os.path.exists("trained_model.yml"):
        model_status = "❌ Modelul lipsește! Adaugă angajați și reantrenează modelul."
    return render_template('index.html', message=message, model_status=model_status)

@app.route('/start_check_in')
def start_check_in():
    result = subprocess.run(
        [sys.executable, 'check_in.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    message = result.stdout.strip() if result.stdout else "❌ Eroare la pontare!"
    return redirect(url_for('index', message=message))

@app.route('/start_check_out')
def start_check_out():
    result = subprocess.run(
        [sys.executable, 'check_out.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    message = result.stdout.strip() if result.stdout else "❌ Eroare la depontare!"
    return redirect(url_for('index', message=message))

@app.route('/delete_today_attendance')
def delete_today_attendance():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE date = ?", (today,))
    conn.commit()
    conn.close()
    return redirect(url_for('index', message=f"🗑️ Pontajele din {today} au fost șterse!"))

@app.route('/attendance')
def list_attendance():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.nume, a.date, a.time_in, a.time_out
        FROM attendance a
        JOIN employees e ON a.user_id = e.id
        ORDER BY a.date DESC
    """)
    records = cursor.fetchall()
    conn.close()
    return render_template('attendance.html', records=records)

@app.route('/employees')
def list_employees():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return render_template('list_employees.html', employees=employees)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        nume = request.form['nume']
        email = request.form['email']
        departament = request.form['departament']
        data_angajarii = request.form['data_angajarii']
        detalii = request.form['detalii']

        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO employees (nume, email, departament, data_angajarii, detalii)
            VALUES (?, ?, ?, ?, ?)
        """, (nume, email, departament, data_angajarii, detalii))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        subprocess.run([sys.executable, "face_capture.py", str(user_id)])
        subprocess.run([sys.executable, "train_model.py"])

        return redirect(url_for('list_employees', success='added'))

    return render_template('add_employee.html')

@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id = ?", (id,))
    cursor.execute("DELETE FROM attendance WHERE user_id = ?", (id,))
    conn.commit()
    conn.close()

    dataset_folder = 'dataset'
    for file in os.listdir(dataset_folder):
        if file.startswith(f"{id}_"):
            os.remove(os.path.join(dataset_folder, file))

    remaining_images = [f for f in os.listdir(dataset_folder) if f.endswith(".jpg")]

    if remaining_images:
        subprocess.run([sys.executable, "train_model.py"])
    else:
        if os.path.exists("trained_model.yml"):
            os.remove("trained_model.yml")

    return redirect(url_for('list_employees', success='deleted'))

@app.route('/update_employee/<int:id>', methods=['GET', 'POST'])
def update_employee(id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        nume = request.form['nume']
        email = request.form['email']
        departament = request.form['departament']
        data_angajarii = request.form['data_angajarii']
        detalii = request.form['detalii']
        cursor.execute("""
            UPDATE employees
            SET nume = ?, email = ?, departament = ?, data_angajarii = ?, detalii = ?
            WHERE id = ?
        """, (nume, email, departament, data_angajarii, detalii, id))
        conn.commit()
        conn.close()
        return redirect(url_for('list_employees', success='updated'))
    else:
        cursor.execute("SELECT * FROM employees WHERE id = ?", (id,))
        employee = cursor.fetchone()
        conn.close()
        return render_template('update_employee.html', employee=employee)

@app.route('/generate_csv')
def generate_csv():
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"raport_{today}.csv"
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.nume, a.date, a.time_in, a.time_out
        FROM attendance a
        JOIN employees e ON a.user_id = e.id
        ORDER BY a.date DESC
    """)
    records = cursor.fetchall()
    conn.close()

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Nume", "Data", "Intrare", "Ieșire"])
        writer.writerows(records)

    return send_file(filename, as_attachment=True)

@app.route('/generate_excel')
def generate_excel():
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"raport_{today}.xlsx"
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.nume, a.date, a.time_in, a.time_out
        FROM attendance a
        JOIN employees e ON a.user_id = e.id
        ORDER BY a.date DESC
    """)
    records = cursor.fetchall()
    conn.close()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Nume", "Data", "Intrare", "Ieșire"])
    for row in records:
        sheet.append(row)
    workbook.save(filename)

    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
