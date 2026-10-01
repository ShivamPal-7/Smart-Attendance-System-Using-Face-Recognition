# 🎓 Smart Attendance System Using Face Recognition

<div *align*="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-green?style=for-the-badge&logo=opencv&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Working%20Prototype-brightgreen?style=for-the-badge)

**A Python desktop application that automates student attendance using real-time face recognition.**  
Built as a Mini Project — I for B.Sc. Computer Science, Sem-IV  
VPM's RZ Shah College, Mulund | University of Mumbai | 2025-2026

[🌐 Live Demo Page](https://shivampal-7.github.io/Smart-Attendance-System-Using-Face-Recognition/) • [📁 Source Code](https://github.com/ShivamPal-7/Smart-Attendance-System-Using-Face-Recognition)

</div>

---

## 📌 About The Project

Traditional attendance systems are slow, error-prone, and allow proxy attendance. This project solves all three problems by using **face recognition** — students are identified automatically by the webcam, and attendance is recorded in a MySQL database with zero manual effort.

> **Workflow:** Faculty Login → Register Student → Capture Face → Train Model → Live Recognition → Auto Mark Attendance → Generate Reports → Email Alerts

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📷 **Real-Time Face Detection** | Haar Cascade Classifier detects faces in live webcam feed |
| 🧠 **Face Recognition** | LBPH algorithm recognizes registered faces |
| 👤 **Student Registration** | Captures 100 face samples per student via webcam |
| ✅ **Auto Attendance Marking** | Marks attendance with date & time on recognition |
| 🗄️ **MySQL Database** | All records stored securely with no duplicates |
| 📊 **Attendance Reports** | View, filter by date/subject, export to Excel |
| 📧 **Email Alerts** | Email notification module for low attendance |
| 🔐 **Faculty/Admin Login** | Role-based secure login system |
| 📈 **Analytics Charts** | Bar charts showing attendance % per student |
| 🎨 **Modern Dark UI** | Clean Tkinter-based dashboard with tab navigation |

---

## 🖼️ Screenshots

### Login Screen
![Login Screen](screenshots/login.png)

### Main Dashboard
![Dashboard](screenshots/dashboard.png)

### Student Registration
![Student Registration](screenshots/register_student.png)

### Live Face Recognition
![Face Recognition](screenshots/recognition.png)

### Attendance Reports
![Attendance Report](screenshots/attendance_report.png)

### Email Alerts Panel
![Email Alerts](screenshots/email_alerts.png)

---

## 🛠️ Tech Stack

```
Language        →  Python 3.12
GUI Framework   →  Tkinter 
Computer Vision →  OpenCV 4.9 (Haar Cascade + LBPH)
Database        →  MySQL 8.0 via XAMPP
Reporting       →  Pandas + OpenPyXL (Excel export)
Visualization   →  Matplotlib (bar charts)
Email           →  smtplib / Gmail SMTP
Image Handling  →  Pillow (PIL)
```

---

## 📂 Project Structure

```
Smart-Attendance-System-Using-Face-Recognition/
│
├── main.py                    ← Entry point — run this
├── config.py                  ← DB & email settings (not in repo)
├── database.sql               ← MySQL schema & seed data
├── requirements.txt           ← Python dependencies
├── HOW_TO_RUN.txt             ← Full setup guide
├── README.md
│
├── modules/
│   ├── database.py                  ← Database connection & helpers
│   ├── register_student.py    ← Face capture & student registration
│   ├── train_model.py         ← LBPH model training
│   ├── recognize_face.py      ← Real-time recognition engine
│   ├── attendance_manager.py  ← Attendance DB operations
│   ├── report_generator.py    ← Excel reports & bar charts
│   └── notification_system.py ← Low-attendance email alerts
│
├── ui/
│   ├── login_window.py        ← Login screen
│   ├── dashboard.py           ← Main dashboard with sidebar
│   └── camera_test.py         ← Camera diagnostics
│
├── data/
│   ├── student_images/        ← Face photos (not in repo — privacy)
│   └── trained_model.yml      ← Trained model (not in repo)
│
└── screenshots/
    ├── login.png
    ├   ── dashboard.png
    ├── register_student.png
    ├── recognition.png
    └── attendance_report.png   ← UI screenshots for README
```

---

## ⚙️ How It Works

```
Step 1  →  Faculty logs in with email & password
Step 2  →  Register a student (name, roll no, class, email)
Step 3  →  Webcam opens → captures 100 face samples automatically
Step 4  →  Click "Train Model" → LBPH model trained on all registered faces
Step 5  →  Click "Mark Attendance" → Select subject → Press START
Step 6  →  Camera detects & recognizes faces in real-time
Step 7  →  Attendance auto-marked in MySQL with date + time
Step 8  →  View reports, export Excel, check analytics charts
Step 9  →  Send email alerts to students below 75% attendance
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- XAMPP (MySQL 8.0)
- Working webcam
- Windows 10/11 recommended

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/ShivamPal-7/Smart-Attendance-System-Using-Face-Recognition.git
cd Smart-Attendance-System-Using-Face-Recognition
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up database**
- Start XAMPP → Start **Apache** and **MySQL**
- Open `http://localhost/phpmyadmin`
- Click **SQL** tab → paste contents of `database.sql` → click **GO**

**4. Configure the app**
```python
# Create config.py with your settings:
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",        # XAMPP default is blank
    "database": "smart_attendance_db"
}
```

**5. Run the application**
```bash
python main.py

```
### Login

```

The application requires a faculty/admin account configured in the
MySQL database.

For security reasons, login credentials are not published in this
repository.

```

> 📄 See [HOW_TO_RUN.txt](HOW_TO_RUN.txt) for the complete setup guide.

---

## 📦 Requirements

```txt
opencv-python==4.9.0.80
opencv-contrib-python==4.9.0.80
mysql-connector-python==8.3.0
numpy==1.26.4
pandas==2.2.2
openpyxl==3.1.2
matplotlib==3.8.4
Pillow==10.3.0
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Schema

```sql
smart_attendance_db
│
├── students        (student_id, name, roll_no, class, email, phone, image_path)
├── faculty         (faculty_id, name, email, password, department)
├── subjects        (subject_id, name, code, semester)
├── attendance      (att_id, student_id, subject_id, date, time, status)
└── notifications   (notif_id, student_id, message, sent_at)
```

---

## 📊 Performance

The system performs real-time face recognition using OpenCV's LBPH
Face Recognizer. Recognition performance depends on lighting,
camera quality, face angle, and the quality and quantity of registered
face samples.

---

## ⚠️ Known Limitations

- Accuracy drops in very low lighting conditions
- Cannot recognize faces with masks (future: mask-aware model)
- No mobile app — desktop only
- No liveness detection (anti-spoofing) yet
- Single camera per session

---

## 🔮 Future Enhancements

- [ ] Integrate FaceNet / ArcFace deep learning model (99%+ accuracy)
- [ ] Add liveness detection (blink / head-nod anti-spoofing)
- [ ] Build Android / iOS mobile companion app
- [ ] Deploy on AWS/GCP for multi-branch college use
- [ ] Add SMS alerts via Twilio
- [ ] Mask-aware face recognition
- [ ] Multi-camera support for large lecture halls

---

## 🔒 Privacy & Security Note

Student face images (`data/student_images/`) and the trained recognition model (`data/trained_model.yml`) are stored **locally only** and are **not included in this repository** for privacy and security reasons.

The `config.py` file containing database credentials is also excluded via `.gitignore`.

---

## 📋 Project Info

| Field | Details |
|-------|---------|
| **Developer** | Shivam Mukhtar Pal |
| **Roll No.** | 2653027 |
| **Course** | B.Sc. Computer Science — Sem V |
| **College** | VPM's RZ Shah College of Arts, Science & Commerce, Mulund |
| **University** | University of Mumbai |
| **Year** | 2026-2027 |
| **Project Type** | Mini Project – I |

---

## 📬 Connect

**Shivam Pal**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/shivam-pal-621767394)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/ShivamPal-7)

---

## 📄 License

This project is developed for academic purposes as part of the B.Sc. Computer Science curriculum at VPM's RZ Shah College, Mulund, affiliated to University of Mumbai.

---

<div align="center">

**⭐ If this project helped you, please give it a star on GitHub!**

*Developed with ❤️ by Shivam Pal*

</div>
