@echo off
title Online Examination System (OES) Local Server
color 0A
cls
echo ======================================================================
echo    APEX INSTITUTE OF ENGINEERING ^& TECHNOLOGY - EXAMINATION PORTAL
echo ======================================================================
echo.
echo [*] Checking local environment...
echo [*] Starting Local Server on your Laptop...
echo.
echo [+] Local Web Access  : http://127.0.0.1:5000
echo [+] Super Admin Login : sharon@oes.com  / Sharon123
echo [+] Student Login     : sumit@oes.com   / Sumit123
echo.
echo [!] Press CTRL+C to stop the server at any time.
echo ======================================================================
echo.

python app.py
pause
