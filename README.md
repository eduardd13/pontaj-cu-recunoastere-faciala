# Face Recognition Attendance System
A facial recognition-based attendance application developed in Python with a Flask web interface. This system allows employees to clock in and out using face detection and recognition.

** Features**
 Employee check-in and check-out using facial recognition.
 Daily attendance records (date, check-in time, check-out time).
 Automatic dataset creation and model training.
 Face recognition powered by OpenCV and LBPH.
 Export reports in CSV and Excel formats.
 Admin panel to:
  - Add new employees (with face capture).
  - Update or delete employee data.
  - View and manage attendance records.
  - Delete daily attendance records.
 Organized project structure for easy maintenance.
------------------------------------------------------------------------------------------------------------------
** Technologies Used **
- Python 3
- Flask (for the web interface)
- OpenCV (face detection and recognition)
- SQLite (database)
- Bootstrap (for styling the web interface)
- Werkzeug (for future password hashing)
- Git (for version control)
- CSV/Excel export with csv and openpyxl libraries.
------------------------------------------------------------------------------------------------------------------
**  How It Works **
Face Capture: When a new employee is added, 20 face images are captured and stored.
Training: The model is trained automatically based on the images in the dataset.
Attendance: Using a webcam, the system recognizes the employee and records the check-in or check-out time.
Duplicate Protection:
An employee cannot check in twice without checking out first.
Multiple shifts per day are allowed.
Record Management: The admin can manage employees and attendance records directly from the web interface.

