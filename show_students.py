import sys
import io
import os

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app import create_app
from models import User

app = create_app()
with app.app_context():
    students = User.query.filter_by(role="student").order_by(User.id.asc()).all()
    print(f"  [+] Total Registered Students Found in Database: {len(students)}\n")
    print(f"  {'ID':<4} | {'Roll Number':<14} | {'Full Name':<20} | {'Department / Branch':<36} | {'Email':<25}")
    print("  " + "=" * 105)
    for s in students:
        print(f"  {s.id:<4} | {str(s.roll_no):<14} | {s.name:<20} | {s.department:<36} | {s.email:<25}")
    print("  " + "=" * 105)
