"""
Student Portal & Live Examination Engine
========================================
Handles student dashboard, live timed interactive exams, anti-cheating tab-switch detection,
automatic grading, instant scorecards, and official downloadable certificates.
"""

import random
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Exam, Question, Attempt, Answer, Subject

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.before_request
@login_required
def check_student_access():
    """Ensure account is active."""
    if not current_user.is_active:
        flash("Your student account has been deactivated. Please contact administration.", "danger")
        return redirect(url_for("auth.logout"))


OFFICIAL_DEPARTMENTS = [
    "Computer Science & Engineering",
    "Information Technology",
    "Artificial Intelligence & Data Science",
    "Electrical Engineering",
    "Cyber Security & Digital Forensics",
    "Biotechnology Engineering",
    "Electronics & Communication Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
]

def normalize_department(dept_name):
    if not dept_name:
        return "Computer Science & Engineering"
    dept_name = dept_name.strip()
    if dept_name in OFFICIAL_DEPARTMENTS:
        return dept_name
    mapping = {
        "Web Development & Full-Stack Systems": "Information Technology",
        "Database Systems & Engineering": "Computer Science & Engineering",
        "Cyber Security & Cloud Infrastructure": "Cyber Security & Digital Forensics",
        "Department of Computer Science & Engineering": "Computer Science & Engineering",
        "CS": "Computer Science & Engineering",
        "IT": "Information Technology",
        "AI": "Artificial Intelligence & Data Science",
        "EE": "Electrical Engineering",
        "ECE": "Electronics & Communication Engineering",
        "ME": "Mechanical Engineering",
        "CE": "Civil Engineering",
    }
    return mapping.get(dept_name, "Computer Science & Engineering")


@student_bp.route("/dashboard")
def dashboard():
    """Student Lobby displaying available exams, recent scores, and certificates strictly tailored to student's department."""
    student_dept = normalize_department(current_user.department)
    if current_user.department != student_dept:
        current_user.department = student_dept
        db.session.commit()

    target_dept = student_dept
    available_exams = Exam.query.filter(
        Exam.is_published == True,
        (Exam.department == target_dept) | (Exam.department == "All Departments")
    ).order_by(Exam.id.asc()).all()
    dept_subjects = Subject.query.filter_by(department=target_dept).all()
    display_dept_title = target_dept

    # Fallback to all published exams only if no department-specific exams exist
    if not available_exams:
        available_exams = Exam.query.filter_by(is_published=True).order_by(Exam.id.asc()).all()
        display_dept_title = "Published Examinations"
    if not dept_subjects:
        dept_subjects = Subject.query.all()

    my_attempts = Attempt.query.filter_by(student_id=current_user.id).order_by(Attempt.started_at.desc()).all()
    stats = current_user.get_stats()
    subjects = Subject.query.all()

    completed_exam_ids = {
        a.exam_id for a in my_attempts if a.status == "completed"
    }

    return render_template(
        "student/dashboard.html",
        exams=available_exams,
        my_attempts=my_attempts,
        completed_exam_ids=completed_exam_ids,
        stats=stats,
        subjects=subjects,
        dept_subjects=dept_subjects,
        selected_dept=target_dept,
        display_dept_title=display_dept_title
    )


@student_bp.route("/exam/<int:exam_id>")
def take_exam(exam_id):
    """
    Live Interactive Examination Interface.
    Enforces fullscreen, countdown timer, question palette, and tab-switch proctoring.
    """
    exam = Exam.query.get_or_404(exam_id)

    if not exam.is_published and not current_user.is_admin:
        flash("This exam is currently not active or unpublished.", "warning")
        return redirect(url_for("student.dashboard"))

    # Check if student already completed this exam
    previous_attempt = Attempt.query.filter_by(
        student_id=current_user.id, exam_id=exam.id, status="completed"
    ).first()

    if previous_attempt and not exam.allow_multiple_attempts:
        flash("You have already completed this official examination.", "info")
        return redirect(url_for("student.view_result", attempt_id=previous_attempt.id))

    # Retrieve or initialize active attempt
    attempt = Attempt.query.filter_by(
        student_id=current_user.id, exam_id=exam.id, status="in_progress"
    ).first()

    if not attempt:
        attempt = Attempt(
            student_id=current_user.id,
            exam_id=exam.id,
            started_at=datetime.utcnow(),
            status="in_progress",
            total_marks=exam.total_marks
        )
        db.session.add(attempt)
        db.session.commit()

    # Calculate remaining time in seconds
    elapsed_seconds = int((datetime.utcnow() - attempt.started_at).total_seconds())
    total_allowed_seconds = exam.duration_minutes * 60
    remaining_seconds = max(0, total_allowed_seconds - elapsed_seconds)

    if remaining_seconds <= 0:
        # Time expired: auto-finalize
        return redirect(url_for("student.submit_exam", exam_id=exam.id))

    # Prepare questions
    questions = list(exam.questions)
    if exam.shuffle_questions:
        # Shuffle with deterministic student seed so refreshing maintains the same order
        rnd = random.Random(current_user.id + exam.id)
        rnd.shuffle(questions)

    return render_template(
        "student/exam_view.html",
        exam=exam,
        attempt=attempt,
        questions=questions,
        remaining_seconds=remaining_seconds,
        total_questions=len(questions)
    )


@student_bp.route("/exam/<int:exam_id>/submit", methods=["POST"])
def submit_exam(exam_id):
    """
    Finalize student exam submission.
    Performs automatic grading, calculates percentage, letter grade, and issues certificate on pass.
    """
    exam = Exam.query.get_or_404(exam_id)

    # Find the current in_progress attempt
    attempt = Attempt.query.filter_by(
        student_id=current_user.id, exam_id=exam.id, status="in_progress"
    ).first()

    if not attempt:
        # Fallback to most recent attempt
        attempt = Attempt.query.filter_by(
            student_id=current_user.id, exam_id=exam.id
        ).order_by(Attempt.id.desc()).first()

    if not attempt:
        flash("No active attempt found for this exam.", "danger")
        return redirect(url_for("student.dashboard"))

    # Capture anti-cheat violations and snapshot
    violations = request.form.get("violations_count", type=int) or 0
    snapshot_data = request.form.get("student_snapshot", "").strip()

    attempt.violations_count = violations
    if snapshot_data:
        attempt.student_snapshot = snapshot_data

    # Clear prior answers for this attempt if any
    Answer.query.filter_by(attempt_id=attempt.id).delete()

    earned_score = 0.0
    correct_count = 0
    wrong_count = 0
    unattempted_count = 0

    for q in exam.questions:
        selected_opt = request.form.get(f"question_{q.id}", "").strip().upper()
        if not selected_opt:
            unattempted_count += 1
            ans = Answer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_option=None,
                is_correct=False,
                marks_awarded=0.0
            )
        elif selected_opt == q.correct_option:
            correct_count += 1
            earned_score += q.marks
            ans = Answer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_option=selected_opt,
                is_correct=True,
                marks_awarded=q.marks
            )
        else:
            wrong_count += 1
            deduction = exam.negative_marks if exam.negative_marks > 0 else 0.0
            earned_score -= deduction
            ans = Answer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_option=selected_opt,
                is_correct=False,
                marks_awarded=-deduction
            )

        db.session.add(ans)

    # Score calculation and bounds
    final_score = max(0.0, round(earned_score, 2))
    total_marks = exam.total_marks or (len(exam.questions) * 1.0)
    percentage = round((final_score / total_marks) * 100, 1) if total_marks > 0 else 0.0

    attempt.score = final_score
    attempt.total_marks = total_marks
    attempt.percentage = percentage
    attempt.grade = Attempt.calculate_grade(percentage)
    attempt.is_passed = (final_score >= exam.passing_marks)
    attempt.status = "completed"
    attempt.submitted_at = datetime.utcnow()

    # Generate verified Certificate ID if student passed
    if attempt.is_passed and not attempt.certificate_id:
        attempt.generate_certificate_id()

    db.session.commit()

    if attempt.is_passed:
        flash(f"🎉 Congratulations {current_user.name}! You passed with {percentage}% ({attempt.grade}). Your certificate is ready!", "success")
    else:
        flash(f"Exam submitted. You scored {final_score} / {total_marks} ({percentage}%).", "info")

    return redirect(url_for("student.view_result", attempt_id=attempt.id))


@student_bp.route("/result/<int:attempt_id>")
def view_result(attempt_id):
    """
    Instant Scorecard & Detailed Question-by-Question Review with Explanations.
    """
    attempt = Attempt.query.get_or_404(attempt_id)

    # Security check: only the student or admin can view
    if attempt.student_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized access to result record.", "danger")
        return redirect(url_for("student.dashboard"))

    answers = Answer.query.filter_by(attempt_id=attempt.id).all()
    correct_count = sum(1 for a in answers if a.is_correct)
    wrong_count = sum(1 for a in answers if not a.is_correct and a.selected_option is not None)
    unattempted_count = sum(1 for a in answers if a.selected_option is None)

    return render_template(
        "student/result_view.html",
        attempt=attempt,
        exam=attempt.exam,
        answers=answers,
        correct_count=correct_count,
        wrong_count=wrong_count,
        unattempted_count=unattempted_count
    )


@student_bp.route("/certificate/<int:attempt_id>")
def download_certificate(attempt_id):
    """
    Official Verified Certificate of Academic Excellence & Achievement.
    High-resolution printable layout with Institute Crest, Grade, QR Verification, and Digital Seal.
    """
    attempt = Attempt.query.get_or_404(attempt_id)

    if attempt.student_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized access to certificate.", "danger")
        return redirect(url_for("student.dashboard"))

    if not attempt.is_passed or not attempt.certificate_id:
        flash("Certificate is only available for successfully passed examinations.", "warning")
        return redirect(url_for("student.view_result", attempt_id=attempt.id))

    return render_template(
        "student/certificate.html",
        attempt=attempt,
        student=attempt.student,
        exam=attempt.exam,
        issue_date=attempt.submitted_at.strftime("%B %d, %Y") if attempt.submitted_at else datetime.utcnow().strftime("%B %d, %Y")
    )


@student_bp.route("/history")
def history():
    """View complete history of past exam attempts and certificates."""
    my_attempts = Attempt.query.filter_by(student_id=current_user.id).order_by(Attempt.submitted_at.desc()).all()
    return render_template("student/history.html", attempts=my_attempts)


@student_bp.route("/announcements")
def announcements():
    """View official broadcasts, new department updates, and academic notices."""
    from models import Notification
    
    student_notifs = Notification.query.filter(
        (Notification.target_role.in_(["student", "all"])) |
        (Notification.target_department == current_user.department) |
        (Notification.target_user_id == current_user.id)
    ).order_by(Notification.created_at.desc()).all()

    # Automatically mark unread as read when student visits announcements page
    for n in student_notifs:
        if not n.is_read:
            n.is_read = True
    db.session.commit()

    return render_template("student/announcements.html", notifications=student_notifs)


@student_bp.route("/api/update-note", methods=["POST"])
def update_note():
    """Save or update student's personal Today Note and status."""
    data = request.get_json(silent=True) or request.form
    note_text = data.get("note", "").strip()
    status_text = data.get("status", "").strip()

    if not note_text:
        return jsonify({"status": "error", "message": "Note content cannot be empty."}), 400

    current_user.custom_note = note_text
    if status_text:
        current_user.note_status = status_text
    current_user.note_updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify({
        "status": "success",
        "note": current_user.custom_note,
        "note_status": current_user.note_status,
        "time_text": "Just now"
    })
