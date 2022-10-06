from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, \
    validators, SelectField, RadioField  # Importing a string forms
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo  # Importing validators for fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, logout_user, login_required , current_user, login_manager, LoginManager


# SQL alchemy - ORM (Object Relational Mapper) for different databases.
# It allows us to access our database in an easy to use object-oriented way.

# .config - set config values on the application.
# A secret key for our application - will protect against modifying cookies, cross-site request forgery attacks, etc.
# Ideally we want the secret key to be some random character, so we can import 'secrets' and use secrets.token_hex(16)
# To get a good random string.
app = Flask(__name__)
app.config['SECRET_KEY'] = '0dd67f6b98b0f1b9b45af215f1e0fe28'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///libraries_db.db'  # Config the location of our database.
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# In order to create our database, we need to use the terminal.
# We go into our venv in our project, and use: "from (py_filename) import (SQLAlchemy_instant)".
# So here we use: "from flaskblogTemplates import db"
# To create the tables we use: "(SQLAlchemy_instant).create_all()"
# So here we use: "db.create_all()".
# To add data, we use: "from (py_filename) import (models_names)".
# So here we use: "from flaskblogTemplates import User, Post"
# Then we can create instants of our models using: "(name) = (model_name)((attributes))".
# For example: "user_1 = User(username='Gal', email='gal@demo.com', password='password')"
# Since 'id' is the PK, if we don't pass an argument it will automatically assign a unique number.
# To save the changes we made, we use: "(SQLAlchemy_instant).session.add((name))".
# So here: "db.session.add(user_1)". This will only save the changes and not write into the DB.
# To write all the changes we use: "(SQLAlchemy_instant).session.commit()".
# In here: "db.session.commit()".
# We can use query methods to get data from the tables: "(model_name).query.(function)".
# For example: "User.query.all()", "User.query.filter_by(username='Gal').all()".
# We can save the query result in an instant, and then access its data and use some built-in functions.
# For example: "user = User.query.filter_by(username='Gal').first()"
# To delete all data in the tables, we use: "(SQLAlchemy_instant).drop_all()".
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(30), nullable=False)
    lastName = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    memberAt = db.relationship('Membership', backref='membership', lazy=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"Member('{self.firstName}', '{self.lastName}', '{self.email}')"


class Library(db.Model):
    libraryName = db.Column(db.String(50), primary_key=True)
    phoneNumber = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    ms_library = db.relationship('Membership', backref='membership_lb', lazy=True)
    book_in_library = db.relationship('BookInLibrary', backref='book_il', lazy=True)

    def __repr__(self):
        return f"Library('{self.libraryName}', '{self.phoneNumber}')"


class Membership(db.Model):
    member_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    library_name = db.Column(db.String(50), db.ForeignKey('library.libraryName'), nullable=False)
    loan_book_memNum = db.relationship('LoanedBook', backref='memberNum', lazy=True)
    loan_book_library = db.relationship('LoanedBook', backref='lbName', lazy=True)

    def __repr__(self):
        return f"Membership('{self.member_number}', '{self.library_name}')"


class Genre(db.Model):
    genre_type = db.Column(db.String(30), primary_key=True)
    book_rl = db.relationship('Book', backref='book_genre', lazy=True)

    def __repr__(self):
        return f"Genre('{self.genre_type}')"


class Book(db.Model):
    bookName = db.Column(db.String(30), primary_key=True)
    authorName = db.Column(db.String(30), nullable=False)
    genre_type = db.Column(db.String(30), db.ForeignKey('genre.genre_type'), nullable=False)
    book_il = db.relationship('BookInLibrary', backref='book', lazy=True)

    def __repr__(self):
        return f"Book('{self.bookName}', '{self.authorName}')"


class BookInLibrary(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_name = db.Column(db.String(30), db.ForeignKey('book.bookName'), nullable=False)
    library_name = db.Column(db.String(50), db.ForeignKey('library.libraryName'), nullable=False)
    loan_book_id = db.relationship('LoanedBook', backref='b_id', lazy=True)


class LoanedBook(db.Model):
    loan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_number = db.Column(db.Integer, db.ForeignKey('membership.member_number'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book_in_library.id'), nullable=False)
    library_name = db.Column(db.String(50), nullable=False)
    # This needs to be a foreign key to BookInLibrary and not Library, but impossible because of multiple foreign keys.
    loan_date = db.Column(db.String(15), nullable=False)
    return_date = db.Column(db.String(15))
    # SQLite doesn't support DateTime type. Needs to be stored as a string.

    def __repr__(self):
        return f"LoanedBook('{self.loan_id}', " \
               f"'{self.member_number}', " \
               f"'{self.book_id}', " \
               f"'{self.library_name}', " \
               f"'{self.loan_date}', " \
               f"'{self.return_date}')"


def library_query():
    return Library.query


class RegisterToLibraryForm(FlaskForm):
    library = QuerySelectField(query_factory=library_query, allow_blank=False, get_label='libraryName')
    submit = SubmitField('Submit')


