import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application Configuration Settings"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "oes-super-secret-key-2026-academics")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'online_exam.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # College / Institute Branding Settings
    INSTITUTE_NAME = "Apex Institute of Engineering & Technology"
    INSTITUTE_SUBTITLE = "Department of Computer Science & Information Technology"
    INSTITUTE_CODE = "AIET-2026"
    SYSTEM_NAME = "Online Examination & Certification Portal"
