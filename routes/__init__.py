"""
Route Blueprints for Online Examination System
"""
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.student import student_bp
from routes.main import main_bp

__all__ = ["auth_bp", "admin_bp", "student_bp", "main_bp"]
