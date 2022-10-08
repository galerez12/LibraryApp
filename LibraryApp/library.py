from flask import render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm, SearchForm, ReturnBookForm
from models import User, Library, Membership, Book, LoanedBook, BookInLibrary, RegisterToLibraryForm
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required , current_user
from init import app, db


# Route for home page
@app.route("/")
@app.route("/home")
def home():
    lb = Library.query.all()  # Getting all the libraries' information to show on home page
    return render_template('libraries.html', libraries=lb)
    # Rendering the template for home page and passing the libraries list


# Route for search page
@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    books = db.session.query(Book, BookInLibrary).join(Book)  # Getting all the books that are in libraries
    if form.validate_on_submit():
        search_field = form.search_by.data  # Checking which field was searched for
        if search_field == 'book':
            # Filtering the table with the book that was searched for and rendering the template with filtered data.
            books = books.filter_by(bookName=form.keyword.data)
            return render_template('books.html', books=books, form=form, lend_book=form)
        elif search_field == 'author':
            # Filtering the table with the author that was searched for and rendering the template with filtered data.
            books = books.filter_by(authorName=form.keyword.data)
            return render_template('books.html', books=books, form=form, lend_book=form)
        elif search_field == 'library':
            # Filtering the table with the library that was searched for and rendering the template with filtered data.
            books = db.session.query(Book, BookInLibrary).join(BookInLibrary).filter_by(library_name=form.keyword.data)
            return render_template('books.html', books=books, form=form, lend_book=form)
        elif search_field == 'genre':
            # Filtering the table with the genre that was searched for and rendering the template with filtered data.
            books = books.filter_by(genre_type=form.keyword.data)
            return render_template('books.html', books=books, form=form, lend_book=form)

    if request.method == "POST":  # If the 'Lend Book' button was pressed then a post request is made
        lend_books()  # Calling the 'lend book' function
        return redirect(url_for('home'))  # Redirecting the user back to home page
    if form.errors != {}:  # Checking for any errors in the form and showing a matching flash messages
        for error in form.errors.values():
            flash(f'Error searching: {error}')

    return render_template('search.html', title='Search', form=form)  # Rendering the search template


# A function for lending books. User must be logged in to enter this page.
@login_required
def lend_books():
    lend_book = request.form.get('lend_book')  # Getting the book id for the requested book
    # Filtering 'LoanedBook' table to check if the requested book is already loaned to someone.
    b = LoanedBook.query.filter_by(book_id=lend_book).filter_by(return_date=None).first()
    if b is None:  # If the books isn't loaned
        requested_book = BookInLibrary.query.filter_by(id=lend_book).first()  # Getting the book id
        user1 = current_user  # Getting the information about the logged user
        current_member = Membership.query.filter_by(member_id=user1.id).first()  # Getting the user's memberships
        # Checking if the user is registered to the library the requested book belongs to
        is_member = Membership.query.filter_by(library_name=requested_book.library_name).first()
        if is_member is None:  # If no info was found the user isn't registered to that library
            flash(f'You are not a member of {requested_book.library_name}. '
                  f'You need to register to the library on order to lend the book {requested_book.book_name}.')
        else:  # The user is registered to the library, creating a new row for the loaned book
            new_lend_book = LoanedBook(member_number=current_member.member_id,
                                       book_id=requested_book.id,
                                       library_name=requested_book.library_name,
                                       loan_date=datetime.today().date())
            db.session.add(new_lend_book)  # Adding the new row to the db
            db.session.commit()  # Committing the changes
            flash(f'You successfully lend the book {new_lend_book.b_id.book_name}')
    else:
        flash('This book is already lend')
    return redirect(url_for('home'))  # Redirecting the user to home page


# Route to register page
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user1 = User.query.filter_by(id=form.id.data).first()  # Checking if the id already exists in db
        if user1 is None:  # If none, then user doesn't exists
            hashed_pw = generate_password_hash(form.password.data, "sha256")  # Generating a hashed password
            # Creating a new user with the data from the user (but with a hashed password)
            user1 = User(id=form.id.data,
                         firstName=form.firstName.data,
                         lastName=form.lastName.data,
                         email=form.email.data,
                         password_hash=hashed_pw)
            db.session.add(user1)  # Adding the new user to the db
            db.session.commit()  # Committing the changes
            login_user(user1)  # Saving the new user as the logged user
            flash(f'Member Added {form.email.data}', 'success')
            return redirect(url_for('register_to_library'))
        else:
            flash("User with that email already exists")
    if form.errors != {}:  # Checking for any errors in the form and showing a matching flash messages
        for error in form.errors.values():
            flash(f'Error creating user: {error}')
    return render_template('register.html', title='Register', form=form)  # Rendering the register template


# Route to 'register to library' page. User must be logged in to enter this page.
@app.route("/registerToLibrary", methods=['GET', 'POST'])
@login_required
def register_to_library():
    form = RegisterToLibraryForm()
    if form.validate_on_submit():
        library_field = form.library.data  # Getting the requested library
        user1 = current_user  # Getting the current user logged in
        # Checking if the user is already registered to the requested library
        member = Membership.query.filter_by(member_id=user1.id, library_name=library_field).first()
        if member is None:  # If the user isn't registered to the library
            member = Membership(member_id=user1.id, library_name=library_field)  # Creating a new membership
            db.session.add(member)  # Adding the new member to the db
            db.session.commit()  # Committing the changes
            flash(f'Successfully registered to {library_field}! Member number: {member.member_number}', 'success')
            return redirect(url_for('home'))  # Redirecting the user to home page
        else:
            flash(f'You are already a member in {library_field}')
    # Rendering the 'register to library' template
    return render_template('registerToLibrary.html', title='Register To Library', form=form)


# Route to login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # Checking if the user exists
        if user:
            # Comparing hashed password to the password the user entered
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)  # Setting the user as the logged user
                flash('You have been logged in!', 'success')
                return redirect(url_for('home'))  # Redirecting the user to home page
            else:
                # Showing a message if the email or password were wrong
                # (a general message in order not to reveal which field was wrong)
                flash('Wrong email or password')
        else:
            flash("User doesn't exists")  # Showing a message if the user doesn't exists
    if form.errors != {}:
        for error in form.errors.values():
            flash(f'Error creating user: {error}')
    return render_template('login.html', title='Login', form=form)  # Rendering the login template


# Route to 'logout' page. User must be logged in to enter this page.
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()  # Logging out the user
    flash("You have been logged out")
    return redirect(url_for('login'))  # Redirecting the client to home page


# Route to 'owned books' page. User must be logged in to enter this page.
@app.route('/ownedBooks', methods=['GET', 'POST'])
@login_required
def owned_books():
    form = ReturnBookForm()
    user1 = current_user  # Getting the information of the logged user
    # Getting the user's memberships information
    current_member = Membership.query.filter_by(member_id=user1.id).first()
    # Getting all the loaned books of the user that weren't returned yet
    b = LoanedBook.query.filter_by(member_number=current_member.member_id).filter_by(return_date=None)
    # If the 'Return Book' button was pressed then a post request is made
    if request.method == "POST":
        return_book = request.form.get('return_book')  # Getting the book id for the requested book
        # Finding the requested book row in database
        book_to_update = LoanedBook.query.filter_by(loan_id=return_book).first()
        # Changing the return date of the requested book for today's date
        book_to_update.return_date = datetime.today().date()
        db.session.commit()  # Committing the changes
        redirect(url_for('home'))  # Redirecting the user to home page
    return render_template('ownedBooks.html', books=b, return_book=form)  # Rendering the 'owned books' template


# Route to user's 'books history' page. User must be logged in to enter this page.
@app.route('/booksHistory', methods=['GET', 'POST'])
@login_required
def books_history():
    user1 = current_user  # Getting the information of the logged user
    # Getting the user's memberships information
    current_member = Membership.query.filter_by(member_id=user1.id).first()
    # Getting the user's loaned books history
    b = LoanedBook.query.filter_by(member_number=current_member.member_id)
    return render_template('booksHistory.html', books=b)  # Rendering the 'books history' template


if __name__ == '__main__':
    app.run(debug=True)

