"""
Comprehensive End-to-End Test Suite for Online Examination System (OES)
"""
import unittest
from app import create_app
from models import db, User, Subject, Question, Exam, Attempt, Answer

class OESFullTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

    def test_01_homepage_and_scrollytelling(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Online Examination", res.data)
        self.assertIn(b"webgl-canvas", res.data)

    def test_02_auth_pages_and_registration(self):
        # Registration page
        res = self.client.get("/auth/register")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Student Registration", res.data)

        # Register new student
        import random
        r_num = f"CS{random.randint(10000, 99999)}"
        email = f"test_{r_num.lower()}@oes.com"
        res_reg = self.client.post("/auth/register", data={
            "name": "Test Candidate",
            "roll_no": r_num,
            "department": "Computer Science & Engineering",
            "email": email,
            "phone": "+91 99999 88888",
            "password": "studentpassword",
            "confirm_password": "studentpassword"
        }, follow_redirects=True)
        with self.app.app_context():
            u = User.query.filter_by(email=email).first()
            if u:
                db.session.delete(u)
                db.session.commit()

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
        # Login as Sumit Kushwaha (22BCS101)
        self.client.post("/auth/login", data={
            "identifier": "sumit@oes.com",
            "password": "Sumit123"
        }, follow_redirects=True)

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
        import random
        rnd = random.randint(10000, 99999)
        email = f"taker_{rnd}@oes.com"
        
        # Register new student with department auto-roll generation
        reg_res = self.client.post("/auth/register", data={
            "department": "Information Technology",
            "name": f"Candidate {rnd}",
            "email": email,
            "phone": "+91 99887 76655",
            "password": "takerpassword",
            "confirm_password": "takerpassword"
        }, follow_redirects=True)

        self.assertEqual(reg_res.status_code, 200)

        with self.app.app_context():
            taker = User.query.filter_by(email=email).first()
            self.assertIsNotNone(taker)
            # Verify auto-generated roll starts with 22BIT
            self.assertTrue(taker.roll_no.startswith("22BIT"))
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

        # Clean up taker attempt and answers and user
        with self.app.app_context():
            u = User.query.filter_by(email=email).first()
            if u:
                attempts = Attempt.query.filter_by(student_id=u.id).all()
                for a in attempts:
                    Answer.query.filter_by(attempt_id=a.id).delete()
                    db.session.delete(a)
                db.session.delete(u)
                db.session.commit()

if __name__ == "__main__":
    unittest.main()
