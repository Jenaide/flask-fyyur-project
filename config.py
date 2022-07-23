import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import *
import psycopg2

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

conn = psycopg2.connect(
    database="fyyur4", user="postgres", password="tamlin", host="localhost", port="5432"
)
cursor = conn.cursor()

cursor.close()
conn.close()

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres=tamlin@localhost:5432/fyyur4'
SQLALCHEMY_TRACK_MODIFICATION = False
SQLALCHEMY_ECHO = True
