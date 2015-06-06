@echo off
pip install -r requirements.txt
copy src\settings\local.py.example src\settings\local.py
pause

