from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm, SearchForm, ReturnBookForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from models import User, Library, Membership, Genre, Book, LoanedBook, BookInLibrary, db, app, RegisterToLibraryForm
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required , current_user

lb = Library.query.all()


@app.route("/")
@app.route("/home")
def home():
    # print(datetime.today().date())
    return render_template('libraries.html', libraries=lb)


@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    books = db.session.query(Book, BookInLibrary).join(Book)
    # books = db.session.query(Book).join(BookInLibrary, Book.bookName == BookInLibrary.book_name)
    # books = db.session.query(Book, BookInLibrary, LoanedBook).join(Book).outerjoin(LoanedBook).filter(or_(LoanedBook.return_date.isnot(None), LoanedBook.loan_id==None))
    # books = books.query.filter_by(LoanedBook.return_date.isnot(None))
    if form.validate_on_submit():
        search_field = form.search_by.data
        if search_field == 'book':
            books = books.filter_by(bookName=form.keyword.data)
            # b = BookInLibrary.query.filter_by(book_name=form.keyword.data).first()
            return render_template('books.html', books=books, form=form, lend_book=form)
        elif search_field == 'author':
            books = books.filter_by(authorName=form.keyword.data)
            # a = Book.query.filter_by(authorName=form.keyword.data)
            # for c in a:
            #     b = BookInLibrary.query.filter_by(book_name=c.bookName).first()
            #     print(b.book.authorName)
            return render_template('books.html', books=books, form=form, lend_book=form)
        elif search_field == 'library':
            books = db.session.query(Book, BookInLibrary).join(BookInLibrary).filter_by(library_name=form.keyword.data)
            # b = BookInLibrary.query.filter_by(library_name=form.keyword.data)
            # print(b.book.authorName)
            return render_template('books.html', books=books, form=form, lend_book=form)
        elif search_field == 'genre':
            books = books.filter_by(genre_type=form.keyword.data)
            # a = Book.query.filter_by(genre_type=form.keyword.data)
            # for c in a:
            #     b = BookInLibrary.query.filter_by(book_name=c.bookName).first()
            #     print(b.book.authorName)
            return render_template('books.html', books=books, form=form, lend_book=form)

    if request.method == "POST":
        loan_books()
        return redirect(url_for('home'))
    if form.errors != {}:
        for error in form.errors.values():
            flash(f'Error searching: {error}')

    return render_template('search.html', title='Search', form=form)


@login_required
def loan_books():
    lend_book = request.form.get('lend_book')
    b = LoanedBook.query.filter_by(book_id=lend_book).filter_by(return_date=None).first()
    if b is None:
        requested_book = BookInLibrary.query.filter_by(id=lend_book).first()
        user1 = current_user
        current_member = Membership.query.filter_by(member_id=user1.id).first()
        is_member = Membership.query.filter_by(library_name=requested_book.library_name).first()
        if is_member is None:
            flash(f'You are not a member of {requested_book.library_name}. '
                  f'You need to register to the library on order to lend the book {requested_book.book_name}.')
        else:
            new_lend_book = LoanedBook(member_number=current_member.member_id,
                                       book_id=requested_book.id,
                                       library_name=requested_book.library_name,
                                       loan_date=datetime.today().date())
            db.session.add(new_lend_book)
            db.session.commit()
            flash(f'Lend Book {new_lend_book.b_id.book_name}')
    else:
        flash('This books is already lend by another member')
    return redirect(url_for('home'))


@app.route("/libraries")
def libraries():
    return render_template('libraries.html', libraries=lb)


# Creating a route for the forms to see how they get converted to HTML.
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user1 = User.query.filter_by(id=form.id.data).first()
        if user1 is None:
            hashed_pw = generate_password_hash(form.password.data, "sha256")
            user1 = User(id=form.id.data,
                         firstName=form.firstName.data,
                         lastName=form.lastName.data,
                         email=form.email.data,
                         password_hash=hashed_pw)
            db.session.add(user1)
            db.session.commit()
            login_user(user1)
            flash(f'Member Added {form.email.data}', 'success')
            return redirect(url_for('register_to_library'))
        else:
            flash("User with that email already exists")
    if form.errors != {}:
        for error in form.errors.values():
            flash(f'Error creating user: {error}')
    return render_template('register.html', title='Register', form=form)


@app.route("/registerToLibrary", methods=['GET', 'POST'])
@login_required
def register_to_library():
    form = RegisterToLibraryForm()
    if form.validate_on_submit():
        user1 = current_user
        member = Membership.query.filter_by(member_id=user1.id, library_name=lb.libraryName).first()
        if member is None:
            member = Membership(member_id=user1.id, library_name=lb.libraryName)
            db.session.add(member)
            db.session.commit()
            flash(f'Successfully registered to {lb.libraryName}! Member number: {member.member_number}', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'You are already a member in {lb.libraryName}')
    return render_template('registerToLibrary.html', title='Register To Library', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('You have been logged in!', 'success')
                return redirect(url_for('register_to_library'))
            else:
                flash('Wrong email or password')
        else:
            flash("User doesn't exists")
    if form.errors != {}:
        for error in form.errors.values():
            flash(f'Error creating user: {error}')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for('login'))


@app.route('/ownedBooks', methods=['GET', 'POST'])
@login_required
def owned_books():
    form = ReturnBookForm()
    user1 = current_user
    current_member = Membership.query.filter_by(member_id=user1.id).first()
    b = LoanedBook.query.filter_by(member_number=current_member.member_id).filter_by(return_date=None)
    if request.method == "POST":
        return_book = request.form.get('return_book')
        book_to_update = LoanedBook.query.filter_by(loan_id=return_book).first()
        book_to_update.return_date = datetime.today().date()
        db.session.commit()
        redirect(url_for('home'))
    return render_template('ownedBooks.html', books=b, return_book=form)


if __name__ == '__main__':
    app.run(debug=True)

