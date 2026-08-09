@echo off
title OES - Enrolled Students Registry
color 0B
cls
echo =========================================================================================================
echo                       ONLINE EXAMINATION SYSTEM - ENROLLED STUDENTS REGISTRY
echo =========================================================================================================
echo.

python show_students.py

echo.
echo =========================================================================================================
echo   Database File Location: %~dp0online_exam.db
echo =========================================================================================================
echo.
pause
