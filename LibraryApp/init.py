from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# An init file to initialize all needed data

app = Flask(__name__)
app.config['SECRET_KEY'] = '0dd67f6b98b0f1b9b45af215f1e0fe28'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///libraries_db.db'  # Config the location of our database.
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



