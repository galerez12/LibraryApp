from library import app
from flask import render_template
from library.models import Book


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/library')
def library_page():
    books = Book.query.all()
    return render_template('library.html', books=books)


@ app.route('/about/<username>')
def about_page(username):
    return f'<h1>About Page {username}</h1>'