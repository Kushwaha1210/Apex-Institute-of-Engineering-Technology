"""
Admin & Faculty Portal Routes
=============================
Handles Admin Dashboard, Enrolled Students Management, Question Bank CRUD,
Exam Creation & Scheduling, Results Analytics, and Merit List CSV Exports.
"""

import io
import csv
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, jsonify
from flask_login import login_required, current_user
from models import db, User, Subject, Question, Exam, Attempt, Answer, exam_questions

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
@login_required
def require_admin():
    """Enforce admin authorization on all routes in this blueprint."""
    if not current_user.is_admin:
        flash("Access denied: Faculty or Administrator privileges required.", "danger")
        return redirect(url_for("student.dashboard"))


@admin_bp.route("/dashboard")
def dashboard():
    """Admin Overview Dashboard with live KPI counters and recent activity."""
    is_super = current_user.is_superadmin
    dept = current_user.department

    if is_super or dept in ["All Departments", None]:
        students_query = User.query.filter_by(role="student")
        exams_query = Exam.query
        attempts_query = Attempt.query.filter_by(status="completed")
    else:
        students_query = User.query.filter_by(role="student", department=dept)
        exams_query = Exam.query.filter((Exam.department == dept) | (Exam.department == "All Departments"))
        attempts_query = Attempt.query.filter_by(status="completed").join(User, Attempt.student_id == User.id).filter(User.department == dept)

    total_students = students_query.count()
    total_questions = Question.query.count()
    total_exams = exams_query.count()
    total_attempts = attempts_query.count()

    completed_attempts = attempts_query.all()
    if completed_attempts:
        avg_score = sum(a.percentage for a in completed_attempts) / len(completed_attempts)
        passed_count = sum(1 for a in completed_attempts if a.is_passed)
        pass_rate = round((passed_count / len(completed_attempts)) * 100, 1)
    else:
        avg_score = 0.0
        pass_rate = 0.0

    recent_students = students_query.order_by(User.created_at.desc()).limit(6).all()
    recent_attempts = attempts_query.order_by(Attempt.submitted_at.desc()).limit(6).all()
    subjects = Subject.query.all()

    return render_template(
        "admin/dashboard.html",
        total_students=total_students,
        total_questions=total_questions,
        total_exams=total_exams,
        total_attempts=total_attempts,
        avg_score=round(avg_score, 1),
        pass_rate=pass_rate,
        recent_students=recent_students,
        recent_attempts=recent_attempts,
        subjects=subjects,
        is_superadmin=is_super,
        admin_department=dept
    )


# ==========================================
# ENROLLED STUDENTS MANAGEMENT
# ==========================================

@admin_bp.route("/students")
def students():
    """
    Real-Time Enrolled Students Table.
    Shows newly registered candidates, their roll numbers, branches, total exams, and scores.
    """
    search_query = request.args.get("q", "").strip()
    department_filter = request.args.get("dept", "").strip()

    is_super = current_user.is_superadmin
    admin_dept = current_user.department

    query = User.query.filter_by(role="student")

    # Scope strictly to HOD department if not Super Admin
    if not is_super and admin_dept and admin_dept != "All Departments":
        query = query.filter(User.department == admin_dept)
        department_filter = admin_dept
    elif department_filter:
        query = query.filter(User.department == department_filter)

    if search_query:
        query = query.filter(
            (User.name.ilike(f"%{search_query}%")) |
            (User.roll_no.ilike(f"%{search_query}%")) |
            (User.email.ilike(f"%{search_query}%"))
        )

    enrolled_students = query.order_by(User.created_at.desc()).all()

    # All 9 Academic Department Domains & Enrolled Branches
    all_dept_set = {
        "Computer Science & Engineering",
        "Information Technology",
        "Artificial Intelligence & Data Science",
        "Cyber Security & Digital Forensics",
        "Electronics & Communication Engineering",
        "Electrical Engineering",
        "Mechanical Engineering",
        "Civil Engineering",
        "Biotechnology Engineering"
    }
    user_depts = [
        d[0] for d in db.session.query(User.department).filter(User.role == "student", User.department.isnot(None)).distinct() if d[0]
    ]
    all_dept_set.update(user_depts)
    departments = sorted(list(all_dept_set))

    return render_template(
        "admin/students.html",
        students=enrolled_students,
        search_query=search_query,
        department_filter=department_filter,
        departments=departments,
        is_superadmin=is_super,
        admin_department=admin_dept
    )


@admin_bp.route("/students/<int:student_id>/toggle-status", methods=["POST"])
def toggle_student_status(student_id):
    """Toggle active/blocked status for a student."""
    student = User.query.get_or_404(student_id)
    if student.role == "student":
        student.is_active = not student.is_active
        db.session.commit()
        status_str = "activated" if student.is_active else "deactivated"
        flash(f"Student account '{student.name}' ({student.roll_no}) has been {status_str}.", "info")
    return redirect(url_for("admin.students"))


@admin_bp.route("/students/<int:student_id>/history")
def student_history(student_id):
    """Get exam attempt history of a specific student (JSON for modal)."""
    student = User.query.get_or_404(student_id)
    attempts = Attempt.query.filter_by(student_id=student.id).order_by(Attempt.started_at.desc()).all()

    data = {
        "student": {
            "name": student.name,
            "roll_no": student.roll_no,
            "department": student.department,
            "email": student.email,
            "phone": student.phone or "N/A",
            "enrolled_date": student.created_at.strftime("%b %d, %Y")
        },
        "attempts": [
            {
                "id": a.id,
                "exam_title": a.exam.title if a.exam else "Unknown Exam",
                "score": f"{a.score} / {a.total_marks}",
                "percentage": f"{a.percentage}%",
                "grade": a.grade,
                "is_passed": a.is_passed,
                "certificate_id": a.certificate_id or "-",
                "date": a.submitted_at.strftime("%b %d, %Y %I:%M %p") if a.submitted_at else "Incomplete",
                "violations": a.violations_count
            }
            for a in attempts
        ]
    }
    return jsonify(data)


@admin_bp.route("/students/<int:student_id>/delete", methods=["POST"])
def delete_student(student_id):
    """Delete a student and their attempt records."""
    student = User.query.get_or_404(student_id)
    if student.role == "student":
        name = student.name
        db.session.delete(student)
        db.session.commit()
        flash(f"Student '{name}' was deleted successfully.", "warning")
    return redirect(url_for("admin.students"))


# ==========================================
# SUPER ADMIN: DEPARTMENTS & HOD DIRECTORY
# ==========================================

@admin_bp.route("/departments")
def departments():
    """Super Admin: Academic Departments & HOD Faculty Management Overview."""
    if not current_user.is_superadmin:
        return redirect(url_for("admin.dashboard"))

    from routes.student import OFFICIAL_DEPARTMENTS
    from routes.auth import BRANCH_CODES

    dept_overview = []
    dept_icons = {
        "Computer Science & Engineering": "💻",
        "Information Technology": "🌐",
        "Artificial Intelligence & Data Science": "🧠",
        "Cyber Security & Digital Forensics": "🛡️",
        "Electronics & Communication Engineering": "📡",
        "Electrical Engineering": "⚡",
        "Mechanical Engineering": "⚙️",
        "Civil Engineering": "🏗️",
        "Biotechnology Engineering": "🧬",
    }

    for d in OFFICIAL_DEPARTMENTS:
        hod = User.query.filter_by(role="admin", department=d).first()
        student_count = User.query.filter_by(role="student", department=d).count()
        exam_count = Exam.query.filter((Exam.department == d) | (Exam.department == "All Departments")).count()
        attempts = Attempt.query.filter_by(status="completed").join(User, Attempt.student_id == User.id).filter(User.department == d).all()
        pass_rate = round((sum(1 for a in attempts if a.is_passed) / len(attempts)) * 100, 1) if attempts else 0.0

        dept_overview.append({
            "name": d,
            "code": BRANCH_CODES.get(d, "ENG"),
            "icon": dept_icons.get(d, "🏛️"),
            "hod": hod,
            "student_count": student_count,
            "exam_count": exam_count,
            "pass_rate": pass_rate
        })

    return render_template("admin/departments.html", departments=dept_overview)


@admin_bp.route("/departments/<string:dept_name>")
def department_detail(dept_name):
    """Super Admin: In-depth Department Profile showing HOD, Enrolled Students, and Exams Data."""
    if not current_user.is_superadmin:
        return redirect(url_for("admin.dashboard"))

    from routes.student import normalize_department, OFFICIAL_DEPARTMENTS
    from routes.auth import BRANCH_CODES

    dept = normalize_department(dept_name)
    hod = User.query.filter_by(role="admin", department=dept).first()
    students = User.query.filter_by(role="student", department=dept).order_by(User.created_at.desc()).all()
    exams = Exam.query.filter((Exam.department == dept) | (Exam.department == "All Departments")).order_by(Exam.created_at.desc()).all()
    subjects = Subject.query.filter((Subject.department == dept) | (Subject.department == "All Departments")).all()
    attempts = Attempt.query.filter_by(status="completed").join(User, Attempt.student_id == User.id).filter(User.department == dept).order_by(Attempt.percentage.desc()).all()

    dept_code = BRANCH_CODES.get(dept, "ENG")

    return render_template(
        "admin/department_detail.html",
        department=dept,
        dept_code=dept_code,
        hod=hod,
        students=students,
        exams=exams,
        subjects=subjects,
        attempts=attempts
    )


# ==========================================
# QUESTION BANK MANAGEMENT (FACULTY HOD SCOPED)
# ==========================================

@admin_bp.route("/questions")
def questions():
    """
    Question Bank Management: Strictly scoped to the logged-in Faculty's department.
    Super Admin is redirected to Departments Management.
    """
    if current_user.is_superadmin:
        flash("Question Bank is managed directly by Department Faculty HODs.", "info")
        return redirect(url_for("admin.departments"))

    admin_dept = current_user.department
    subject_id = request.args.get("subject_id", type=int)
    difficulty = request.args.get("difficulty", "").strip()
    search = request.args.get("q", "").strip()

    # Only load subjects belonging to the faculty's department (or All Departments)
    subjects = Subject.query.filter(
        (Subject.department == admin_dept) | (Subject.department == "All Departments")
    ).order_by(Subject.name).all()
    
    valid_subject_ids = [s.id for s in subjects]

    query = Question.query.filter(Question.subject_id.in_(valid_subject_ids))

    if subject_id and subject_id in valid_subject_ids:
        query = query.filter_by(subject_id=subject_id)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if search:
        query = query.filter(Question.question_text.ilike(f"%{search}%"))

    question_list = query.order_by(Question.created_at.desc()).all()

    return render_template(
        "admin/questions.html",
        questions=question_list,
        subjects=subjects,
        selected_subject_id=subject_id,
        selected_difficulty=difficulty,
        search_query=search,
        admin_department=admin_dept
    )


@admin_bp.route("/questions/new", methods=["POST"])
def add_question():
    """Add a new MCQ question to the question bank."""
    subject_id = request.form.get("subject_id", type=int)
    question_text = request.form.get("question_text", "").strip()
    option_a = request.form.get("option_a", "").strip()
    option_b = request.form.get("option_b", "").strip()
    option_c = request.form.get("option_c", "").strip()
    option_d = request.form.get("option_d", "").strip()
    correct_option = request.form.get("correct_option", "A").strip().upper()
    difficulty = request.form.get("difficulty", "Medium").strip()
    explanation = request.form.get("explanation", "").strip()
    marks = request.form.get("marks", type=float) or 1.0

    if not subject_id or not question_text or not option_a or not option_b or not option_c or not option_d:
        flash("Please fill in all required question and option fields.", "warning")
        return redirect(url_for("admin.questions"))

    q = Question(
        subject_id=subject_id,
        question_text=question_text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_option=correct_option,
        difficulty=difficulty,
        explanation=explanation,
        marks=marks
    )
    db.session.add(q)
    db.session.commit()
    flash("Question successfully added to the Question Bank!", "success")
    return redirect(url_for("admin.questions", subject_id=subject_id))


@admin_bp.route("/questions/<int:question_id>/edit", methods=["POST"])
def edit_question(question_id):
    """Update question content, options, and difficulty."""
    q = Question.query.get_or_404(question_id)
    q.subject_id = request.form.get("subject_id", type=int)
    q.question_text = request.form.get("question_text", "").strip()
    q.option_a = request.form.get("option_a", "").strip()
    q.option_b = request.form.get("option_b", "").strip()
    q.option_c = request.form.get("option_c", "").strip()
    q.option_d = request.form.get("option_d", "").strip()
    q.correct_option = request.form.get("correct_option", "A").strip().upper()
    q.difficulty = request.form.get("difficulty", "Medium").strip()
    q.explanation = request.form.get("explanation", "").strip()
    q.marks = request.form.get("marks", type=float) or 1.0

    db.session.commit()
    flash("Question updated successfully!", "success")
    return redirect(url_for("admin.questions"))


@admin_bp.route("/questions/<int:question_id>/delete", methods=["POST"])
def delete_question(question_id):
    """Delete a question from the question bank."""
    q = Question.query.get_or_404(question_id)
    db.session.delete(q)
    db.session.commit()
    flash("Question removed from bank.", "info")
    return redirect(url_for("admin.questions"))


# ==========================================
# EXAM BUILDER & MANAGEMENT
# ==========================================

@admin_bp.route("/exams")
def exams():
    """Exam Management: view, create, toggle publish, and configure rules."""
    is_super = current_user.is_superadmin
    admin_dept = current_user.department
    dept_filter = request.args.get("dept", "").strip()

    from routes.student import OFFICIAL_DEPARTMENTS

    if is_super or admin_dept in ["All Departments", None]:
        if dept_filter and dept_filter != "All":
            all_exams = Exam.query.filter(Exam.department == dept_filter).order_by(Exam.created_at.desc()).all()
        else:
            all_exams = Exam.query.order_by(Exam.created_at.desc()).all()
    else:
        all_exams = Exam.query.filter((Exam.department == admin_dept) | (Exam.department == "All Departments")).order_by(Exam.created_at.desc()).all()

    subjects = Subject.query.order_by(Subject.name).all()
    questions = Question.query.all()
    return render_template(
        "admin/exams.html",
        exams=all_exams,
        subjects=subjects,
        questions=questions,
        is_superadmin=is_super,
        admin_department=admin_dept,
        official_departments=OFFICIAL_DEPARTMENTS,
        selected_dept_filter=dept_filter
    )


@admin_bp.route("/exams/new", methods=["POST"])
def create_exam():
    """Create a new exam with duration, passing marks, negative marks, and questions."""
    from datetime import timedelta
    
    title = request.form.get("title", "").strip()
    subject_id = request.form.get("subject_id", type=int)
    description = request.form.get("description", "").strip()
    duration_minutes = request.form.get("duration_minutes", type=int) or 30
    passing_marks = request.form.get("passing_marks", type=float) or 10.0
    negative_marks = request.form.get("negative_marks", type=float) or 0.0
    allow_multiple = bool(request.form.get("allow_multiple_attempts"))
    shuffle_questions = bool(request.form.get("shuffle_questions"))
    require_webcam = bool(request.form.get("require_webcam"))
    is_published = bool(request.form.get("is_published"))
    selected_question_ids = request.form.getlist("question_ids")

    if not title or not subject_id:
        flash("Exam Title and Subject are required.", "warning")
        return redirect(url_for("admin.exams"))

    # Set department: either from form, from subject, or default to HOD's department
    exam_dept = request.form.get("department", "").strip()
    subject = db.session.get(Subject, subject_id) if hasattr(db.session, 'get') else Subject.query.get(subject_id)
    if not exam_dept or exam_dept == "inherit":
        if subject and subject.department:
            exam_dept = subject.department
        elif not current_user.is_superadmin and current_user.department and current_user.department != "All Departments":
            exam_dept = current_user.department
        else:
            exam_dept = "Computer Science & Engineering"

    # Idempotency guard: prevent duplicate submission within 10 seconds
    ten_sec_ago = datetime.utcnow() - timedelta(seconds=10)
    recent_dup = Exam.query.filter(
        Exam.title == title,
        Exam.subject_id == subject_id,
        Exam.department == exam_dept,
        Exam.created_by == current_user.id,
        Exam.created_at >= ten_sec_ago
    ).first()
    if recent_dup:
        flash(f"Exam '{title}' was already created a moment ago.", "info")
        return redirect(url_for("admin.exams"))

    # If no questions selected manually, auto-include all questions from the chosen subject
    if not selected_question_ids:
        subject_qs = Question.query.filter_by(subject_id=subject_id).all()
        selected_questions = subject_qs
    else:
        selected_questions = Question.query.filter(Question.id.in_([int(qid) for qid in selected_question_ids])).all()

    total_marks = sum(q.marks for q in selected_questions) if selected_questions else 25.0

    exam = Exam(
        title=title,
        subject_id=subject_id,
        department=exam_dept,
        description=description,
        duration_minutes=duration_minutes,
        total_marks=total_marks,
        passing_marks=passing_marks,
        negative_marks=negative_marks,
        allow_multiple_attempts=allow_multiple,
        shuffle_questions=shuffle_questions,
        require_webcam=require_webcam,
        is_published=is_published,
        created_by=current_user.id
    )
    exam.questions = selected_questions
    db.session.add(exam)
    db.session.commit()

    flash(f"Exam '{title}' successfully created for {exam_dept} with {len(selected_questions)} questions!", "success")
    return redirect(url_for("admin.exams"))


@admin_bp.route("/exams/<int:exam_id>/toggle-publish", methods=["POST"])
def toggle_exam_publish(exam_id):
    """Toggle whether an exam is visible to students."""
    exam = Exam.query.get_or_404(exam_id)
    exam.is_published = not exam.is_published
    db.session.commit()
    status = "published" if exam.is_published else "hidden"
    flash(f"Exam '{exam.title}' is now {status} for students.", "info")
    return redirect(url_for("admin.exams"))


@admin_bp.route("/exams/<int:exam_id>/delete", methods=["POST"])
def delete_exam(exam_id):
    """Delete an exam and associated attempt records."""
    exam = Exam.query.get_or_404(exam_id)
    title = exam.title
    db.session.delete(exam)
    db.session.commit()
    flash(f"Exam '{title}' deleted successfully.", "warning")
    return redirect(url_for("admin.exams"))


# ==========================================
# SUBJECTS & CUSTOM DOMAIN MANAGEMENT
# ==========================================

@admin_bp.route("/subjects/new", methods=["POST"])
def add_subject():
    """Create a new custom subject in the system."""
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip().upper()
    description = request.form.get("description", "").strip()
    icon = request.form.get("icon", "📚").strip()

    if not name or not code:
        flash("Subject Name and Code are required.", "warning")
        return redirect(url_for("admin.questions"))

    if Subject.query.filter_by(code=code).first():
        flash(f"Subject code '{code}' already exists.", "danger")
        return redirect(url_for("admin.questions"))

    subj_dept = request.form.get("department", "").strip() or (current_user.department if current_user.department != "All Departments" else "All Departments")
    subj = Subject(name=name, code=code, department=subj_dept, description=description, icon=icon)
    db.session.add(subj)
    db.session.commit()
    flash(f"Subject '{name}' created successfully for {subj_dept}!", "success")
    return redirect(url_for("admin.questions"))


# ==========================================
# RESULTS & MERIT LIST CSV EXPORT
# ==========================================

@admin_bp.route("/results")
def results():
    """Master Results Sheet & Candidate Performance Leaderboard."""
    exam_id = request.args.get("exam_id", type=int)
    subject_id = request.args.get("subject_id", type=int)

    is_super = current_user.is_superadmin
    admin_dept = current_user.department

    query = Attempt.query.filter_by(status="completed")

    # If department admin, only show results for students in their department
    if not is_super and admin_dept and admin_dept != "All Departments":
        query = query.join(User, Attempt.student_id == User.id).filter(User.department == admin_dept)

    if exam_id:
        query = query.filter(Attempt.exam_id == exam_id)
    if subject_id:
        query = query.join(Exam, Attempt.exam_id == Exam.id).filter(Exam.subject_id == subject_id)

    all_attempts = query.order_by(Attempt.percentage.desc(), Attempt.submitted_at.asc()).all()
    exams_list = Exam.query.order_by(Exam.title).all()
    subjects_list = Subject.query.order_by(Subject.name).all()

    return render_template(
        "admin/results.html",
        attempts=all_attempts,
        exams=exams_list,
        subjects=subjects_list,
        selected_exam_id=exam_id,
        selected_subject_id=subject_id
    )


@admin_bp.route("/results/export-csv")
def export_csv():
    """Export the complete results merit list as a downloadable CSV spreadsheet."""
    exam_id = request.args.get("exam_id", type=int)
    query = Attempt.query.filter_by(status="completed")
    if exam_id:
        query = query.filter_by(exam_id=exam_id)

    attempts = query.order_by(Attempt.percentage.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Student Name", "Roll Number", "Department", "Email",
        "Exam Title", "Score", "Total Marks", "Percentage", "Grade",
        "Result Status", "Certificate ID", "Date Submitted", "Violations Count"
    ])

    for rank, att in enumerate(attempts, 1):
        writer.writerow([
            rank,
            att.student.name if att.student else "N/A",
            att.student.roll_no if att.student else "N/A",
            att.student.department if att.student else "N/A",
            att.student.email if att.student else "N/A",
            att.exam.title if att.exam else "N/A",
            att.score,
            att.total_marks,
            f"{att.percentage}%",
            att.grade,
            "PASSED" if att.is_passed else "FAILED",
            att.certificate_id or "N/A",
            att.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if att.submitted_at else "N/A",
            att.violations_count
        ])

    csv_data = output.getvalue()
    filename = f"OES_Merit_List_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


# ==============================================================================
# Announcement Broadcasting & Notification Management
# ==============================================================================

@admin_bp.route("/announcements", methods=["GET", "POST"])
def announcements():
    """Faculty Announcement Broadcaster & Notifications Feed."""
    from models import Notification
    from routes.auth import BRANCH_CODES

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()
        target_department = request.form.get("target_department", "").strip() or None
        priority = request.form.get("priority", "normal").strip()

        if not title or not message:
            flash("Please provide both an announcement title and detailed notice message.", "warning")
        else:
            notif = Notification(
                title=title,
                message=message,
                category="announcement",
                priority=priority,
                sender_name=current_user.name or "Faculty Administration",
                target_role="student",
                target_department=target_department,
                is_read=False
            )
            db.session.add(notif)
            db.session.commit()
            flash("📢 Announcement successfully broadcasted to all enrolled students!", "success")
            return redirect(url_for("admin.announcements"))

    all_announcements = Notification.query.filter_by(category="announcement").order_by(Notification.created_at.desc()).all()
    all_admin_notifications = Notification.query.filter(
        (Notification.target_role.in_(["admin", "all"])) | 
        (Notification.target_user_id == current_user.id)
    ).order_by(Notification.created_at.desc()).all()

    return render_template(
        "admin/announcements.html",
        announcements=all_announcements,
        admin_notifications=all_admin_notifications,
        departments=list(BRANCH_CODES.keys())
    )


@admin_bp.route("/announcements/delete/<int:announcement_id>", methods=["POST"])
def delete_announcement(announcement_id):
    """Delete / Revoke a broadcasted announcement."""
    from models import Notification
    notif = Notification.query.get_or_404(announcement_id)
    db.session.delete(notif)
    db.session.commit()
    flash("Announcement removed successfully.", "info")
    return redirect(url_for("admin.announcements"))


@admin_bp.route("/api/notifications/mark-read", methods=["POST"])
def mark_notifications_read():
    """AJAX API to mark all unread notifications as read for current user."""
    from models import Notification
    try:
        if current_user.is_admin:
            unread = Notification.query.filter(
                (Notification.target_role.in_(["admin", "all"])) |
                (Notification.target_user_id == current_user.id)
            ).filter_by(is_read=False).all()
        else:
            unread = Notification.query.filter(
                (Notification.target_role.in_(["student", "all"])) |
                (Notification.target_department == current_user.department) |
                (Notification.target_user_id == current_user.id)
            ).filter_by(is_read=False).all()

        for n in unread:
            n.is_read = True
        db.session.commit()
        return jsonify({"status": "success", "marked": len(unread)})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
