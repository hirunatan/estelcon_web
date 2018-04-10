#!/bin/sh

sudo apt install libffi-dev

sudo -H pip3 install pipenv

pipenv install

cp settings/local.py.example settings/local.py

mkdir media

cp -R media.example/* media

cp db.sqlite3.example db.sqlite3

echo Pulsar intro...
read

