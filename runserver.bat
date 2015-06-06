@echo off
set PYTHON_DIR="C:\WinPython-32bit-2.7.9.5"
set PATH=%PYTHON_DIR%;%PATH%
cd src
python manage.py runserver
pause

