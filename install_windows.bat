@echo off
pip install -r requirements.txt
cd src
copy src\settings\local.py.example src\settings\local.py
pause

