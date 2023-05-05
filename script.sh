#!/bin/bash

pip install --force-reinstall -r requirements.txt

export FLASK_APP=main.py
export SECRET_KEY=web-netschool-key

flask run
