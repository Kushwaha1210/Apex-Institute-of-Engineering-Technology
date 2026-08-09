import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app import create_app
from models import db, User, Attempt, Answer, Notification

app = create_app()
with app.app_context():
    # Only keep authorized Admins and Sumit Kushwaha
    keep_emails = [
        'sharon@oes.com',
        'bhushan@oes.com',
        'hod.cse@oes.com',
        'hod.aids@oes.com',
        'hod.cyber@oes.com',
        'hod.ece@oes.com',
        'hod.ee@oes.com',
        'hod.me@oes.com',
        'hod.ce@oes.com',
        'hod.bt@oes.com',
        'sumit@oes.com'
    ]
    
    users_to_delete = User.query.filter(~User.email.in_(keep_emails)).all()
    print(f"[*] Found {len(users_to_delete)} dummy / test student accounts to remove.")
    
    for u in users_to_delete:
        print(f"  [-] Deleting user: {u.name} ({u.email}, Roll: {u.roll_no})")
        attempts = Attempt.query.filter_by(student_id=u.id).all()
        for a in attempts:
            Answer.query.filter_by(attempt_id=a.id).delete()
            db.session.delete(a)
        try:
            Notification.query.filter_by(target_user_id=u.id).delete()
        except Exception:
            pass
        db.session.delete(u)
    
    db.session.commit()
    print("[+] Cleanup complete!")
    
    all_users = User.query.all()
    print(f"\n[+] Total Active Users Remaining ({len(all_users)}):")
    for u in all_users:
        print(f"  • [{u.role.upper()}] {u.name} | {u.email} | Roll: {u.roll_no}")
