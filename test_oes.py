"""
Comprehensive End-to-End Test Suite for Online Examination System (OES)
Uses isolated In-Memory SQLite database (:memory:) so the local dev database is NEVER modified.
"""
import unittest
import random
from config import Config
from app import create_app
from models import db, User, Subject, Question, Exam, Attempt, Answer


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class OESFullTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

            # Seed Admin
            admin = User(
                name="Prof. Bhushan Chaudhari",
                roll_no="FAC_IT01",
                department="Information Technology",
                email="bhushan@oes.com",
                phone="+91 98765 43210",
                role="admin",
                is_active=True
            )
            admin.set_password("Bhushan123")
            db.session.add(admin)

            # Seed Student
            student = User(
                name="Sumit Kushwaha",
                roll_no="22BCS101",
                department="Computer Science & Engineering",
                email="sumit@oes.com",
                phone="+91 98111 22334",
                role="student",
                is_active=True
            )
            student.set_password("Sumit123")
            db.session.add(student)

            # Seed Subject
            sub = Subject(
                name="Python Programming",
                code="PYTHON",
                description="Test Subject",
                icon="🐍",
                department="Information Technology"
            )
            db.session.add(sub)
            db.session.flush()

            # Seed Exam
            exam = Exam(
                title="Python Assessment Test",
                subject_id=sub.id,
                department="Information Technology",
                duration_minutes=30,
                total_marks=10.0,
                passing_marks=4.0,
                negative_marks=0.0,
                is_published=True,
                created_by=admin.id
            )
            db.session.add(exam)
            db.session.flush()

            # Seed Questions
            q1 = Question(
                subject_id=sub.id,
                question_text="What is the output of type(1)?",
                option_a="int",
                option_b="str",
                option_c="float",
                option_d="bool",
                correct_option="A",
                marks=5.0,
                explanation="1 is an integer in Python.",
                difficulty="Easy"
            )
            q2 = Question(
                subject_id=sub.id,
                question_text="Which keyword defines a function in Python?",
                option_a="function",
                option_b="def",
                option_c="func",
                option_d="lambda",
                correct_option="B",
                marks=5.0,
                explanation="def is used to define functions in Python.",
                difficulty="Easy"
            )
            db.session.add_all([q1, q2])
            db.session.flush()

            exam.questions.append(q1)
            exam.questions.append(q2)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_01_homepage_and_scrollytelling(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Online Examination", res.data)

    def test_02_auth_pages_and_registration(self):
        # Registration page
        res = self.client.get("/auth/register")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Candidate", res.data)

        # Register new student
        r_num = f"CS{random.randint(10000, 99999)}"
        email = f"test_{r_num.lower()}@oes.com"
        res_reg = self.client.post("/auth/register", data={
            "name": "Test Candidate",
            "department": "Computer Science & Engineering",
            "email": email,
            "phone": "+91 99999 88888",
            "password": "studentpassword",
            "confirm_password": "studentpassword"
        }, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)
        # Should redirect to login page with success flash
        self.assertIn(b"Enrollment successful", res_reg.data)

    def test_03_admin_portal_and_management(self):
        # Login as admin Prof. Bhushan Chaudhari
        res_login = self.client.post("/auth/login", data={
            "identifier": "bhushan@oes.com",
            "password": "Bhushan123"
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Faculty Control Center", res_login.data)

        # Enrolled Students
        res_stud = self.client.get("/admin/students")
        self.assertEqual(res_stud.status_code, 200)
        self.assertIn(b"Enrolled Students Registry", res_stud.data)

        # Question Bank
        res_q = self.client.get("/admin/questions")
        self.assertEqual(res_q.status_code, 200)
        self.assertIn(b"Question Bank Management", res_q.data)

        # Exam Management
        res_ex = self.client.get("/admin/exams")
        self.assertEqual(res_ex.status_code, 200)
        self.assertIn(b"Exam Builder & Scheduling", res_ex.data)

        # Results & CSV Export
        res_res = self.client.get("/admin/results")
        self.assertEqual(res_res.status_code, 200)
        self.assertIn(b"Examination Results", res_res.data)

        res_csv = self.client.get("/admin/results/export-csv")
        self.assertEqual(res_csv.status_code, 200)
        self.assertEqual(res_csv.mimetype, "text/csv")
        self.assertIn(b"Student Name", res_csv.data)

    def test_04_student_exam_taking_and_certification(self):
        # Login as Sumit Kushwaha
        res_login = self.client.post("/auth/login", data={
            "identifier": "sumit@oes.com",
            "password": "Sumit123"
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)

        # Access Lobby
        res_lobby = self.client.get("/student/dashboard")
        self.assertEqual(res_lobby.status_code, 200)
        self.assertIn(b"Examination Lobby", res_lobby.data)

        # Access History
        res_hist = self.client.get("/student/history")
        self.assertEqual(res_hist.status_code, 200)
        self.assertIn(b"My Scorecards & Certificates", res_hist.data)

    def test_05_exam_taking_submission_and_instant_scoring(self):
        self.client.get("/auth/logout")
        rnd = random.randint(10000, 99999)
        email = f"taker_{rnd}@oes.com"
        
        # Register new student
        self.client.post("/auth/register", data={
            "department": "Information Technology",
            "name": f"Candidate {rnd}",
            "email": email,
            "phone": "+91 99887 76655",
            "password": "takerpassword",
            "confirm_password": "takerpassword"
        }, follow_redirects=True)

        # Login as the new student
        login_res = self.client.post("/auth/login", data={
            "identifier": email,
            "password": "takerpassword"
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        with self.app.app_context():
            exam = Exam.query.filter_by(is_published=True).first()
            self.assertIsNotNone(exam)
            exam_id = exam.id
            q_list = list(exam.questions)

        # Open exam view
        res_exam_page = self.client.get(f"/student/exam/{exam_id}")
        self.assertEqual(res_exam_page.status_code, 200)

        # Submit answers
        submission_data = {
            "violations_count": "0",
            "student_snapshot": ""
        }
        for q in q_list:
            submission_data[f"question_{q.id}"] = q.correct_option

        res_submit = self.client.post(f"/student/exam/{exam_id}/submit", data=submission_data, follow_redirects=True)
        self.assertEqual(res_submit.status_code, 200)
        self.assertIn(b"Examination Scorecard", res_submit.data)
        self.assertIn(b"Congratulations, You Passed", res_submit.data)


if __name__ == "__main__":
    unittest.main()
