#!/bin/sh
sudo pip install -r requirements.txt
cp src/settings/local.py.example src/settings/local.py
cp db.sqlite3.example db.sqlite3

