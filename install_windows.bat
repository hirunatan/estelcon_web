@echo off
cd src
pip install -r requirements.txt
copy src\settings\local.py.example src\settings\local.py
pause

