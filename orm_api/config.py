import os

REGEX_NAME = "^[a-zA-Zа-яА-ЯёЁ0-9 ()-]+$"
REGEX_TITLE = REGEX_NAME
REGEX_INT = "^[0-9]+$"

# SQLALCHEMY_ECHO = True
MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
MYSQL_PASS = os.environ.get('MYSQL_PASS') or 'Password'
MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
MYSQL_BASE = os.environ.get('MYSQL_BASE') or 'asterisk'
SQLALCHEMY_DATABASE_URL = f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}/{MYSQL_BASE}'
