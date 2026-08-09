"""
Database Models for Online Examination System (OES)
===================================================
Defines the relational schema using SQLAlchemy for Users, Subjects, Questions,
Exams, Student Attempts, and Question-wise Answers.
"""

from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """
    User model representing registered candidates (Students) and Faculty (Admin).
    Stores enrollment details, roll numbers, branch, and credentials.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll_no = db.Column(db.String(50), unique=True, nullable=True, index=True)
    department = db.Column(db.String(100), default="Computer Science & Engineering")
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="student")  # 'student' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    custom_note = db.Column(db.Text, default="Going to the evaluation hall and planning official exams for the semester ahead 🏀")
    note_status = db.Column(db.String(50), default="I'm going")
    note_updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attempts = db.relationship("Attempt", backref="student", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        """Hash and set user password securely using Werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the password against stored hash."""
        return check_password_hash(self.password_hash, password)

    # Flask-Login Integration Attributes
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_admin(self):
        return self.role in ["admin", "superadmin"]

    @property
    def is_superadmin(self):
        return self.role == "superadmin"

    def get_id(self):
        return str(self.id)

    def get_stats(self):
        """Get summary statistics for student performance."""
        completed_attempts = self.attempts.filter_by(status="completed").all()
        total_attempts = len(completed_attempts)
        if total_attempts == 0:
            return {
                "total_attempts": 0,
                "passed_attempts": 0,
                "failed_attempts": 0,
                "average_score": 0.0,
                "certificates_earned": 0
            }
        
        passed = sum(1 for a in completed_attempts if a.is_passed)
        avg_score = sum(a.percentage for a in completed_attempts) / total_attempts
        certs = sum(1 for a in completed_attempts if a.is_passed and a.certificate_id)
        
        return {
            "total_attempts": total_attempts,
            "passed_attempts": passed,
            "failed_attempts": total_attempts - passed,
            "average_score": round(avg_score, 1),
            "certificates_earned": certs
        }


class Subject(db.Model):
    """
    Academic Subjects (e.g. Python, DBMS, DSA, Operating Systems, Computer Networks).
    Categorizes the question bank and published examinations.
    """
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    department = db.Column(db.String(100), default="Computer Science & Engineering")
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default="📚")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    questions = db.relationship("Question", backref="subject", lazy="dynamic", cascade="all, delete-orphan")
    exams = db.relationship("Exam", backref="subject", lazy="dynamic", cascade="all, delete-orphan")


# Many-to-Many Association Table between Exams and Questions
exam_questions = db.Table(
    "exam_questions",
    db.Column("exam_id", db.Integer, db.ForeignKey("exams.id", ondelete="CASCADE"), primary_key=True),
    db.Column("question_id", db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True)
)


class Question(db.Model):
    """
    Question Bank Item. Multiple-Choice Question with 4 options, difficulty rating,
    verified answer, and detailed explanation.
    """
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_option = db.Column(db.String(5), nullable=False)  # 'A', 'B', 'C', 'D'
    difficulty = db.Column(db.String(20), default="Medium")   # 'Easy', 'Medium', 'Hard'
    explanation = db.Column(db.Text, nullable=True)
    marks = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Secondary relationship with Exams
    exams = db.relationship("Exam", secondary=exam_questions, back_populates="questions")


class Exam(db.Model):
    """
    Published or Scheduled Examination with duration limits, passing marks,
    negative marking rules, and anti-cheating configuration.
    """
    __tablename__ = "exams"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    department = db.Column(db.String(100), default="Computer Science & Engineering")
    description = db.Column(db.Text, nullable=True)
    duration_minutes = db.Column(db.Integer, default=30)
    total_marks = db.Column(db.Float, default=25.0)
    passing_marks = db.Column(db.Float, default=10.0)
    negative_marks = db.Column(db.Float, default=0.0)  # e.g., 0.25 per wrong answer
    allow_multiple_attempts = db.Column(db.Boolean, default=False)
    shuffle_questions = db.Column(db.Boolean, default=True)
    require_webcam = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    questions = db.relationship("Question", secondary=exam_questions, back_populates="exams")
    attempts = db.relationship("Attempt", backref="exam", lazy="dynamic", cascade="all, delete-orphan")

    def get_stats(self):
        """Compute live metrics for faculty dashboard."""
        all_attempts = self.attempts.filter_by(status="completed").all()
        total = len(all_attempts)
        if total == 0:
            return {
                "total_attempts": 0,
                "passed_count": 0,
                "failed_count": 0,
                "pass_rate": 0.0,
                "average_score": 0.0,
                "highest_score": 0.0,
                "lowest_score": 0.0
            }
        
        scores = [a.percentage for a in all_attempts]
        passed = sum(1 for a in all_attempts if a.is_passed)
        
        return {
            "total_attempts": total,
            "passed_count": passed,
            "failed_count": total - passed,
            "pass_rate": round((passed / total) * 100, 1),
            "average_score": round(sum(scores) / total, 1),
            "highest_score": round(max(scores), 1),
            "lowest_score": round(min(scores), 1)
        }


class Attempt(db.Model):
    """
    Student Examination Attempt.
    Tracks start/end time, scores, proctoring violations, and official certificate ID.
    """
    __tablename__ = "attempts"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, default=0.0)
    total_marks = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    grade = db.Column(db.String(10), default="F")
    is_passed = db.Column(db.Boolean, default=False)
    certificate_id = db.Column(db.String(50), unique=True, nullable=True, index=True)
    student_snapshot = db.Column(db.Text, nullable=True)  # Base64 snapshot for identity verification
    violations_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="in_progress")  # 'in_progress', 'completed', 'terminated'

    # Relationships
    answers = db.relationship("Answer", backref="attempt", lazy="dynamic", cascade="all, delete-orphan")

    def generate_certificate_id(self):
        """Generate a unique verified certificate code for passing candidates."""
        unique_suffix = uuid.uuid4().hex[:6].upper()
        import random
        att_num = self.id if self.id is not None else random.randint(1000, 9999)
        self.certificate_id = f"OES-2026-CERT-{att_num:04d}-{unique_suffix}"
        return self.certificate_id

    @staticmethod
    def calculate_grade(percentage):
        """Calculate letter grade based on percentage."""
        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B+"
        elif percentage >= 60:
            return "B"
        elif percentage >= 50:
            return "C"
        elif percentage >= 40:
            return "D"
        else:
            return "F"


class Answer(db.Model):
    """
    Individual response submitted by a student for a question within an attempt.
    """
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_option = db.Column(db.String(5), nullable=True)  # 'A', 'B', 'C', 'D' or None
    is_correct = db.Column(db.Boolean, default=False)
    marks_awarded = db.Column(db.Float, default=0.0)

    # Relationship
    question = db.relationship("Question")


class Notification(db.Model):
    """
    Notification & Academic Announcement Model.
    Supports:
    - Admin alerts when a new student enrolls
    - Faculty broadcast announcements to all students or specific departments
    - Department, exam publishing, and schedule updates
    """
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default="announcement")  # 'announcement', 'registration', 'department', 'exam'
    priority = db.Column(db.String(20), default="normal")  # 'normal', 'high', 'urgent'
    sender_name = db.Column(db.String(120), default="Faculty Administration")
    target_role = db.Column(db.String(30), default="student")  # 'all', 'student', 'admin'
    target_department = db.Column(db.String(100), nullable=True)  # None for all departments
    target_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref=db.backref("notifications", lazy="dynamic", cascade="all, delete-orphan"))

    @property
    def time_ago(self):
        """Human-readable relative time string."""
        now = datetime.utcnow()
        diff = now - self.created_at
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        elif seconds < 604800:
            return f"{seconds // 86400}d ago"
        else:
            return self.created_at.strftime("%b %d, %Y")
