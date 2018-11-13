from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine

app = Flask(__name__)
app.config.from_object(Config)
# db = SQLAlchemy(app)
login = LoginManager(app)
bootstrap = Bootstrap(app)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)


from app import routes, models