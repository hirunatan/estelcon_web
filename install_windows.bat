@echo off
pip install -r requirements.txt
copy src\settings\local.py.example src\settings\local.py
copy db.sqlite3.example db.sqlite3
pause

