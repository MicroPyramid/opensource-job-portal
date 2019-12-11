#!/bin/bash
ls /home/peeljobs
pip3 install -r /home/peeljobs/requirements.txt
python3 /home/peeljobs/manage.py migrate
python3 /home/peeljobs/manage.py runserver