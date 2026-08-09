"""
Online Examination System (OES) - Main Application Factory
==========================================================
Initializes Flask application, SQLAlchemy ORM, Flask-Login authentication,
registers blueprints for Auth, Faculty Admin, Student Exam Engine, and Landing Scrollytelling.
"""

from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in with your credentials to access the examination portal."
login_manager.login_message_category = "info"


def create_app(config_class=Config):
    """
    Application Factory: Configures and creates the Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Context processors for global template helpers & real-time notifications
    @app.context_processor
    def inject_global_settings():
        from flask_login import current_user
        from models import Notification
        
        unread_count = 0
        recent_notifs = []
        if current_user.is_authenticated:
            try:
                if current_user.is_admin:
                    notifs_query = Notification.query.filter(
                        (Notification.target_role.in_(["admin", "all"])) |
                        (Notification.target_user_id == current_user.id)
                    ).order_by(Notification.created_at.desc())
                else:
                    notifs_query = Notification.query.filter(
                        (Notification.target_role.in_(["student", "all"])) |
                        (Notification.target_department == current_user.department) |
                        (Notification.target_user_id == current_user.id)
                    ).order_by(Notification.created_at.desc())
                
                recent_notifs = notifs_query.limit(6).all()
                unread_count = notifs_query.filter_by(is_read=False).count()
            except Exception:
                unread_count = 0
                recent_notifs = []

        return {
            "INSTITUTE_NAME": app.config.get("INSTITUTE_NAME", "Apex Institute of Engineering & Technology"),
            "INSTITUTE_SUBTITLE": app.config.get("INSTITUTE_SUBTITLE", "Department of Computer Science & Information Technology"),
            "SYSTEM_NAME": app.config.get("SYSTEM_NAME", "Online Examination System"),
            "INSTITUTE_CODE": app.config.get("INSTITUTE_CODE", "AIET-2026"),
            "unread_notifications_count": unread_count,
            "recent_notifications": recent_notifs
        }

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.student import student_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # Auto-initialize database tables within application context
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    import sys, io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    app = create_app()
    print("=" * 60)
    print("[*] Online Examination System (OES) Server Starting...")
    print("[+] Local Access: http://127.0.0.1:5000")
    print("[+] Admin Credentials: admin@oes.com / admin123")
    print("[+] Demo Student:      aarav@oes.com / student123")
    print("=" * 60)
    app.run(debug=True, port=5000)
