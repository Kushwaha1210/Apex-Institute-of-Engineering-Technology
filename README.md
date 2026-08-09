<div align="center">

# 🏛️ Apex Institute of Engineering & Technology
### Next-Gen Online Examination & Academic Governance System (OES)

[![Live Demo](https://img.shields.io/badge/🚀_Live_Portal-Visit_Website-33BC65?style=for-the-badge&logo=render&logoColor=white)](https://apex-institute-of-engineering-technology.onrender.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/Framework-Flask_3.0-black.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite / SQLAlchemy](https://img.shields.io/badge/Database-SQLAlchemy_ORM-red.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlalchemy.org/)

<p align="center">
  <b>🌐 Live Application URL:</b> <a href="https://apex-institute-of-engineering-technology.onrender.com">https://apex-institute-of-engineering-technology.onrender.com</a>
</p>

</div>

---

## 🌟 Key Features & Architecture

- **🏛️ 9 Engineering Academic Disciplines**: Complete department-scoped workflows for CSE, IT, AI&DS, Cyber Security, ECE, EE, Mechanical, Civil, and Biotechnology.
- **🛡️ Real-Time Proctoring & Anti-Cheat**: Tab switch detection, full-screen lock enforcement, copy-paste prevention, and automatic violation logging.
- **⏱️ Automated Live Grading Engine**: Instant multi-criteria score evaluation with negative marking penalty support and pass/fail thresholds.
- **📜 Cryptographically Verifiable Certificates**: Auto-generated certificates with unique QR codes and verification IDs upon exam passing.
- **👑 Hierarchical Role-Based Access Control (RBAC)**:
  - **Super Admin (Dean):** Global governance, 9-department roster metrics, and HOD management.
  - **Faculty HOD:** Department-scoped Question Bank, exam builder, and student attempt monitoring.
  - **Student Portal:** Adaptive exam interface, real-time timer, syllabus preview, and performance analytics.
- **✨ Ultra-Modern UI & WebGL Particle Aesthetics**: Responsive dark glassmorphism, 3D perspective coverflow carousels, and scrollytelling.

---

## 🔑 Demo Access Credentials (Live Portal)

You can explore all user roles directly on the [Live Portal](https://apex-institute-of-engineering-technology.onrender.com/login):

| Role | Name & Designation | Email / Roll No | Password |
| :--- | :--- | :--- | :--- |
| **👑 Super Admin** | Dr. Sharon Samuel *(Dean of Academics)* | `sharon@oes.com` | `Sharon123` |
| **🌐 IT Faculty HOD** | Prof. Bhushan Chaudhari *(HOD Information Tech)* | `bhushan@oes.com` | `Bhushan123` |
| **💻 CSE Faculty HOD** | Dr. Rajesh Sharma *(HOD Computer Science)* | `rajesh@oes.com` | `Rajesh123` |
| **🎓 Student** | Sumit Kushwaha *(CSE Student)* | `sumit@oes.com` | `Sumit123` |
| **🎓 New Student** | *Self Registration* | [Register New Account](https://apex-institute-of-engineering-technology.onrender.com/register) | *(Your Choice)* |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask, Flask-Login, Flask-SQLAlchemy, Werkzeug
- **WSGI / Production:** Gunicorn, Render Cloud PaaS
- **Database:** SQLite / SQLAlchemy ORM (ACID Compliant)
- **Frontend:** Vanilla HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), Three.js / WebGL Canvas

---

## 💻 Local Development Setup

```bash
# 1. Clone Repository
git clone https://github.com/Kushwaha1210/Apex-Institute-of-Engineering-Technology.git
cd Apex-Institute-of-Engineering-Technology

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Initialize Database & Seed Baseline Dataset
python seed_data.py

# 4. Start Local Development Server
python app.py
```

Open `http://127.0.0.1:5000` in your web browser.

---

<div align="center">
  <sub>Built with ❤️ by <b>Sumit Kushwaha</b> for Apex Institute of Engineering & Technology</sub>
</div>
