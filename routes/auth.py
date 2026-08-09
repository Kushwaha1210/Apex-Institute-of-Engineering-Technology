"""
Authentication & Student Enrollment Routes with Auto-Roll Number Generation
===========================================================================
Handles:
1. Department-based sequential roll number auto-generation (e.g. 22BCS101, 22BIT102)
2. Live roll number preview API for dynamic registration UX
3. Secure user login (via Email or Roll Number) and role-based routing (Admin vs Student)
4. Profile details and password updates
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Department to Official Branch Code Mapping
BRANCH_CODES = {
    "Computer Science & Engineering": "BCS",
    "Information Technology": "BIT",
    "Artificial Intelligence & Data Science": "BAI",
    "Electrical Engineering": "BEE",
    "Cyber Security & Digital Forensics": "BCY",
    "Biotechnology Engineering": "BBT",
    "Electronics & Communication Engineering": "BEC",
    "Mechanical Engineering": "BME",
    "Civil Engineering": "BCE",
}

DEFAULT_BATCH = "22"  # Batch 2022-2026 Academic Code


def generate_next_roll_no(department, batch=DEFAULT_BATCH):
    """
    Auto-generates sequential roll number based on Department / Branch and Batch.
    Format: <Batch><BranchCode><SequentialNumber> (e.g. 22BCS101, 22BIT102, 22BIT103)
    """
    branch_code = BRANCH_CODES.get(department, "BCS")
    prefix = f"{batch}{branch_code}"

    # Query all students having roll numbers starting with this prefix
    existing_students = User.query.filter(User.roll_no.like(f"{prefix}%")).all()

    highest_seq = 100
    for s in existing_students:
        if s.roll_no and s.roll_no.startswith(prefix):
            suffix = s.roll_no[len(prefix):]
            if suffix.isdigit():
                num = int(suffix)
                if num > highest_seq:
                    highest_seq = num

    return f"{prefix}{highest_seq + 1}"


@auth_bp.route("/api/preview-roll-no")
def preview_roll_no():
    """AJAX endpoint for real-time roll number generation when department is selected."""
    dept = request.args.get("dept", "Computer Science & Engineering").strip()
    next_roll = generate_next_roll_no(dept)
    return jsonify({
        "status": "success",
        "department": dept,
        "roll_no": next_roll,
        "branch_code": BRANCH_CODES.get(dept, "BCS"),
        "batch": DEFAULT_BATCH
    })


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle Student & Admin Login by Email, Roll Number, or Full Name."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()  # Email, Roll No, or Name
        password = request.form.get("password", "").strip()
        remember = bool(request.form.get("remember"))

        if not identifier or not password:
            flash("Please provide both identifier (Email/Roll No/Name) and password.", "danger")
            return render_template("auth/login.html")

        # Flexible Case-Insensitive Lookup: By Email OR Roll Number OR Full Name
        from sqlalchemy import func
        user = User.query.filter(
            (func.lower(User.email) == identifier.lower()) |
            (func.lower(User.roll_no) == identifier.lower()) |
            (func.lower(User.name) == identifier.lower())
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Your account has been deactivated. Please contact the administrator.", "danger")
                return render_template("auth/login.html")

            login_user(user, remember=remember)
            flash(f"Welcome back, {user.name}!", "success")

            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)

            if user.is_admin:
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("student.dashboard"))
        else:
            flash("Invalid email/roll number/name or password. Please check your credentials.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle New Student Registration / Enrollment with Department-First Auto-Roll Number Generation.
    Saves student credentials into database and displays them on the Admin Enrolled Students dashboard.
    """
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        department = request.form.get("department", "").strip()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Form Validation
        if not name or not department or not email or not password:
            flash("Please fill in all required fields (Department, Name, Email, Password).", "warning")
            return render_template("auth/register.html", departments=list(BRANCH_CODES.keys()))

        if password != confirm_password:
            flash("Passwords do not match. Please re-enter.", "danger")
            return render_template("auth/register.html", departments=list(BRANCH_CODES.keys()))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return render_template("auth/register.html", departments=list(BRANCH_CODES.keys()))

        # Check existing email
        if User.query.filter_by(email=email).first():
            flash(f"Email '{email}' is already registered! Please log in instead.", "danger")
            return render_template("auth/register.html", departments=list(BRANCH_CODES.keys()))

        # Auto-generate next sequential roll number based on Department in atomic order
        roll_no = generate_next_roll_no(department)

        # Create new Student user
        new_student = User(
            name=name,
            roll_no=roll_no,
            department=department,
            email=email,
            phone=phone,
            role="student",
            is_active=True
        )
        new_student.set_password(password)

        try:
            db.session.add(new_student)
            db.session.flush()

            # Generate Real-Time Notification for Admin Faculty
            from models import Notification
            admin_notif = Notification(
                title=f"🎓 New Student Enrolled: {name}",
                message=f"Candidate {name} ({email}) has enrolled in {department}. Assigned Roll Number: {roll_no}.",
                category="registration",
                priority="normal",
                sender_name="Enrollment Engine",
                target_role="admin"
            )
            db.session.add(admin_notif)
            db.session.commit()

            flash(f"Enrollment successful! Your allocated Roll Number is {roll_no}. Please log in with your credentials.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while creating your account. Please try again.", "danger")

    # Initial auto-roll preview for first department
    initial_dept = list(BRANCH_CODES.keys())[0]
    initial_roll = generate_next_roll_no(initial_dept)

    return render_template(
        "auth/register.html",
        departments=list(BRANCH_CODES.keys()),
        initial_dept=initial_dept,
        initial_roll=initial_roll
    )


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out current user and redirect to home."""
    logout_user()
    flash("You have been safely logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """View and update student/admin profile."""
    if request.method == "POST":
        current_user.name = request.form.get("name", current_user.name).strip()
        current_user.phone = request.form.get("phone", current_user.phone).strip()
        if not current_user.is_admin:
            current_user.department = request.form.get("department", current_user.department).strip()

        new_password = request.form.get("new_password", "").strip()
        if new_password:
            if len(new_password) >= 6:
                current_user.set_password(new_password)
                flash("Profile and password updated successfully!", "success")
            else:
                flash("Password must be at least 6 characters.", "warning")
        else:
            flash("Profile details updated successfully!", "success")

        db.session.commit()
        return redirect(url_for("auth.profile"))

    stats = current_user.get_stats() if not current_user.is_admin else None
    return render_template("auth/profile.html", user=current_user, stats=stats)
