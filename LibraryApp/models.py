from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from init import db, login_manager


# Loading the current user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# A class for 'User' table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # ID - primary key
    firstName = db.Column(db.String(30), nullable=False)  # firstName - cannot be null
    lastName = db.Column(db.String(30), nullable=False)  # lastName - cannot be null
    email = db.Column(db.String(120), unique=True, nullable=False)  # email - must be unique and cannot be null
    # password_hash - the hashed password of the user, cannot be null
    password_hash = db.Column(db.String(128), nullable=False)
    # Relationship definition to 'Membership' table
    memberAt = db.relationship('Membership', backref='membership', lazy=True)

    @property
    def password(self):
        # Showing a message that the password data cannot be shown for security matters
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)  # Generating a hashed password and setting it to self

    def verify_password(self, password):
        # Comparing the hashed password to the password that was entered
        return check_password_hash(self.password_hash, password)

    # Representation of the user
    def __repr__(self):
        return f"User('{self.firstName}', '{self.lastName}', '{self.email}')"


# A class for 'Library' table
class Library(db.Model):
    libraryName = db.Column(db.String(50), primary_key=True)  # libraryName - primary key
    phoneNumber = db.Column(db.String(10), nullable=False)  # phoneNumber - cannot be null
    address = db.Column(db.String(50), nullable=False)  # address - cannot be null
    # Relationship definition to 'Membership' table
    ms_library = db.relationship('Membership', backref='membership_lb', lazy=True)
    # Relationship definition to 'BookInLibrary' table
    book_in_library = db.relationship('BookInLibrary', backref='book_il', lazy=True)

    # Representation of the library
    def __repr__(self):
        return f"Library('{self.libraryName}', '{self.phoneNumber}, {self.address}')"


# A class for 'Membership' table
class Membership(db.Model):
    member_number = db.Column(db.Integer, primary_key=True, autoincrement=True)  # member_number - primary key
    # member_id - foreign key to User's id, cannot be null
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # library_name - foreign key to Library's name, cannot be null
    library_name = db.Column(db.String(50), db.ForeignKey('library.libraryName'), nullable=False)
    # Relationship definition to 'LoanedBook' table
    loan_book_memNum = db.relationship('LoanedBook', backref='memberNum', lazy=True)

    # Representation of the member
    def __repr__(self):
        return f"Membership('{self.member_number}', '{self.library_name}')"


# A class for 'Genre' table
class Genre(db.Model):
    genre_type = db.Column(db.String(30), primary_key=True)  # genre_type - primary key
    # Relationship definition to 'Book' table
    book_rl = db.relationship('Book', backref='book_genre', lazy=True)

    # Representation of the genre
    def __repr__(self):
        return f"Genre('{self.genre_type}')"


# A class for 'Book' table
class Book(db.Model):
    bookName = db.Column(db.String(30), primary_key=True)  # bookName - primary key
    authorName = db.Column(db.String(30), nullable=False)  # authorName-  cannot be null
    # genre_type - foreign key to genre's type, cannot be null
    genre_type = db.Column(db.String(30), db.ForeignKey('genre.genre_type'), nullable=False)
    # Relationship definition to 'BookInLibrary' table
    book_il = db.relationship('BookInLibrary', backref='book', lazy=True)

    # Representation of the book
    def __repr__(self):
        return f"Book('{self.bookName}', '{self.authorName}')"


# A class for 'BookInLibrary' table
class BookInLibrary(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id - autoincrement primary key
    # book_name - foreign key to book's name, cannot be null
    book_name = db.Column(db.String(30), db.ForeignKey('book.bookName'), nullable=False)
    # library_name - foreign key to library's name, cannot be null
    library_name = db.Column(db.String(50), db.ForeignKey('library.libraryName'), nullable=False)
    # Relationship definition to 'LoanedBook' table
    loan_book_id = db.relationship('LoanedBook', backref='b_id', lazy=True)

    # Representation of the book in library
    def __repr__(self):
        return f"BookInLibrary('{self.id}', '{self.bookName}', '{self.library_name}')"


# A class for 'LoanedBook' table
class LoanedBook(db.Model):
    loan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # loan_id - autoincrement primary key
    # member_number - foreign key to membership's member number, cannot be null
    member_number = db.Column(db.Integer, db.ForeignKey('membership.member_number'), nullable=False)
    # book_id - foreign key to book in library's id, cannot be null
    book_id = db.Column(db.Integer, db.ForeignKey('book_in_library.id'), nullable=False)
    # library_name - cannot be null
    # This needs to be a foreign key to BookInLibrary's library name field,
    # but impossible because of SQLAlchemy unable to handle multiple foreign keys
    library_name = db.Column(db.String(50), nullable=False)
    # SQLite doesn't support DateTime type, so needs to be stored as a string.
    loan_date = db.Column(db.String(15), nullable=False)  # loan_date - cannot be null
    return_date = db.Column(db.String(15))  # return_date - can be null, will update when book is returned

    # Representation of the loaned book
    def __repr__(self):
        return f"LoanedBook('{self.loan_id}', " \
               f"'{self.member_number}', " \
               f"'{self.book_id}', " \
               f"'{self.library_name}', " \
               f"'{self.loan_date}', " \
               f"'{self.return_date}')"


# A function for returning all libraries' names
def library_query():
    db_libraries = Library.query.all()  # Query to get the libraries
    libraries = []  # Creating a list that will hold the libraries' names
    for lib in db_libraries:
        libraries.append(lib.libraryName)  # Appending the library's name to the list
    return libraries


# A form for register to library page
# This form is in models.py and not in forms.py due to circular imports
class RegisterToLibraryForm(FlaskForm):
    library = SelectField('Library Name', choices=library_query())
    submit = SubmitField('Submit')


