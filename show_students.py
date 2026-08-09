import sys
import io
import os
import urllib.request
import json

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app import create_app
from models import db, User

RENDER_URL = "https://apex-institute-of-engineering-technology.onrender.com/api/sync/students"

app = create_app()

def sync_online_students():
    """Fetches students from live Render website and syncs them into local online_exam.db."""
    print("  [*] Connecting to live server (Render)...")
    try:
        req = urllib.request.Request(
            RENDER_URL, 
            headers={"User-Agent": "OES-Desktop-Client/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                remote_students = data.get("students", [])
                
                synced_count = 0
                with app.app_context():
                    for rs in remote_students:
                        email = rs.get("email")
                        if not email:
                            continue
                        local_user = User.query.filter_by(email=email).first()
                        if not local_user:
                            # Create and save in local database
                            new_s = User(
                                name=rs.get("name", "Unknown"),
                                roll_no=rs.get("roll_no"),
                                department=rs.get("department", "Computer Science & Engineering"),
                                email=email,
                                phone=rs.get("phone"),
                                role="student",
                                is_active=rs.get("is_active", True)
                            )
                            # Default fallback password for synced student
                            new_s.set_password("Student123")
                            db.session.add(new_s)
                            synced_count += 1
                    
                    if synced_count > 0:
                        db.session.commit()
                        print(f"  [+] Successfully synced {synced_count} new student(s) from online Render website into your local folder!")
                    else:
                        print("  [+] Local folder is already up-to-date with live server.")
    except Exception as e:
        print(f"  [!] Note: Could not connect to live Render server ({e}). Displaying local records:")

# 1. First sync online students
sync_online_students()

# 2. Display all registered students from local database
with app.app_context():
    students = User.query.filter_by(role="student").order_by(User.id.asc()).all()
    print(f"\n  [+] Total Registered Students Found: {len(students)}\n")
    print(f"  {'ID':<4} | {'Roll Number':<14} | {'Full Name':<20} | {'Department / Branch':<36} | {'Email':<25}")
    print("  " + "=" * 105)
    for s in students:
        print(f"  {s.id:<4} | {str(s.roll_no):<14} | {s.name:<20} | {s.department:<36} | {s.email:<25}")
    print("  " + "=" * 105)
