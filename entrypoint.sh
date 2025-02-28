#!/bin/bash
ls /home/peeljobs
pip3 install pipenv
cd /home/peejobs
pipenv install
python3 /home/peeljobs/manage.py migrate
python3 /home/peeljobs/manage.py runserver