@echo off
set PYTHON_DIR="C:\WinPython-32bit-2.7.9.5"
set PATH=%PYTHON_DIR%;%PATH%
pip install -r requirements.txt
copy src\settings\local.py.example src\settings\local.py
pause

