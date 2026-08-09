import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import create_app
from models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text('ALTER TABLE users ADD COLUMN custom_note TEXT DEFAULT "Going to the evaluation hall and planning official exams for the semester ahead 🏀"'))
        db.session.commit()
        print("[+] Added custom_note column successfully.")
    except Exception as e:
        print("[*] custom_note status:", e)

    try:
        db.session.execute(text('ALTER TABLE users ADD COLUMN note_status TEXT DEFAULT "I\'m going"'))
        db.session.commit()
        print("[+] Added note_status column successfully.")
    except Exception as e:
        print("[*] note_status status:", e)

    try:
        db.session.execute(text('ALTER TABLE users ADD COLUMN note_updated_at DATETIME'))
        db.session.commit()
        print("[+] Added note_updated_at column successfully.")
    except Exception as e:
        print("[*] note_updated_at status:", e)
