import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    db_username = os.environ.get('db_username') or 'root'
    db_password = os.environ.get('db_password') or 'root'
    db_host = os.environ.get('db_host') or '127.0.0.1'
    db_lib = os.environ.get('db_lib') or 'wsntest'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql://%s:%s@%s/%s' % (db_username, db_password, db_host, db_lib)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
