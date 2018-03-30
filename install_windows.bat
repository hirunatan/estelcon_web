pip install -r requirements.txt

copy settings\local.py.example settings\local.py

mkdir media

xcopy media.example media /s

copy db.sqlite3.example db.sqlite3

pause

