import os
import pymysql
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key'
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:qwertyuiop@localhost:3306/Cosmestics'
    SQLALCHEMY_DATABASE_URI = "postgresql://pz2244:2048@35.196.158.126/proj1part2"
    ITEM_PER_PAGE = 20