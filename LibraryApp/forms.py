from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, validators, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


# A form class for the registration page.
# Length validators are set because of the limitations in the DB.
class RegistrationForm(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired(), validators.NumberRange(min=1, max=9999999999)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    firstName = StringField('First Name', validators=[DataRequired(), Length(max=30)])
    lastName = StringField('Last Name', validators=[DataRequired(), Length(max=30)])
    submit = SubmitField('Sign Up')


# A form class for the login page.
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# A form class for searching page.
class SearchForm(FlaskForm):
    keyword = StringField('Search', validators=[DataRequired()])
    search_by = SelectField('Search By', choices=[('book', 'Book'),
                                                  ('author', 'Author'),
                                                  ('library', 'Library'),
                                                  ('genre', 'Genre')],
                            render_kw={'style': 'width: 9ch'})
    submit = SubmitField('Submit')


# A form class for 'My Books' page where you can return books.
class ReturnBookForm(FlaskForm):
    submit = SubmitField('Return This Book')










