"""
Main & Scrollytelling Landing Page Routes
=========================================
Features the WebGL 3D Interactive Particle Background and Scrollytelling
academic showcase with live system metrics and course universe.
"""

from flask import Blueprint, render_template
from flask_login import current_user
from models import Subject, Exam, Question, User, Attempt

main_bp = Blueprint("main", __name__)

DEPARTMENTS_DATA = [
    {
        "name": "Computer Science & Engineering",
        "code": "BCS",
        "icon": "💻",
        "description": "Algorithms, Data Structures, Operating Systems, Cloud Architecture, and Software Engineering.",
        "tag": "Core Curriculum • 2026 Batch"
    },
    {
        "name": "Information Technology",
        "code": "BIT",
        "icon": "🌐",
        "description": "Full-Stack Web Systems, Computer Networks, Database Engineering, and Information Security.",
        "tag": "Full-Stack • DevOps"
    },
    {
        "name": "Artificial Intelligence & Data Science",
        "code": "BAI",
        "icon": "🧠",
        "description": "Machine Learning, Deep Neural Networks, Data Analytics, Python Computing, and Predictive Modeling.",
        "tag": "Machine Learning • AI"
    },
    {
        "name": "Cyber Security & Digital Forensics",
        "code": "BCY",
        "icon": "🛡️",
        "description": "Network Defense, Cryptography, Penetration Testing, Ethical Hacking, and Threat Intelligence.",
        "tag": "Security • Forensics"
    },
    {
        "name": "Electronics & Communication Engineering",
        "code": "BEC",
        "icon": "📡",
        "description": "Embedded Systems, VLSI Design, Signal Processing, IoT Telecommunications, and Microcontrollers.",
        "tag": "Embedded • VLSI"
    },
    {
        "name": "Electrical Engineering",
        "code": "BEE",
        "icon": "⚡",
        "description": "Power Systems, Control Engineering, Circuit Analysis, Renewable Energy, and Smart Grids.",
        "tag": "Power Systems • Energy"
    },
    {
        "name": "Mechanical Engineering",
        "code": "BME",
        "icon": "⚙️",
        "description": "Thermodynamics, Strength of Materials, Kinematics, CAD/CAM Design, and Fluid Machinery.",
        "tag": "Robotics • CAD/CAM"
    },
    {
        "name": "Civil Engineering",
        "code": "BCE",
        "icon": "🏗️",
        "description": "Structural Analysis, Geotechnical Surveying, Concrete Technology, and Urban Infrastructure.",
        "tag": "Structural • Urban Design"
    },
    {
        "name": "Biotechnology Engineering",
        "code": "BBT",
        "icon": "🧬",
        "description": "Bioinformatics, Genetic Engineering, Molecular Biology, Bioprocess, and Cellular Systems.",
        "tag": "Genetics • Bio-Tech"
    },
]


@main_bp.route("/")
def index():
    """Interactive 3D WebGL & Scrollytelling Landing Page."""
    total_students = User.query.filter_by(role="student").count()
    total_questions = Question.query.count()
    total_exams = Exam.query.filter_by(is_published=True).count()
    total_certificates = Attempt.query.filter_by(is_passed=True).count()
    subjects = Subject.query.order_by(Subject.name).all()

    return render_template(
        "index.html",
        total_students=total_students,
        total_questions=total_questions,
        total_exams=total_exams,
        total_certificates=total_certificates,
        subjects=subjects,
        departments=DEPARTMENTS_DATA
    )
