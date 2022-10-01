from flask_sqlalchemy import SQLAlchemy
from library import db

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    firstName = db.Column(db.String(length=30), nullable=False)
    lastName = db.Column(db.String(length=30), nullable=False)
    email = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    books = db.relationship('Book', backref='owned_user', lazy=True)


class Book(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=20), nullable=False, unique=True)
    author = db.Column(db.String(length=30), nullable=False)
    genere = db.Column(db.String(length=20), nullable=False)
    total_amount = db.Column(db.Integer(), nullable=False)
    avaliable_amount = db.Column(db.Integer(), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
        return f'{self.name}'

