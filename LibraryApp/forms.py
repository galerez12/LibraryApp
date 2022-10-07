from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, \
    validators, SelectField, RadioField  # Importing a string forms
from wtforms_sqlalchemy.fields import QueryRadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo  # Importing validators for fields


class RegistrationForm(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired(), validators.NumberRange(min=1, max=9999999999)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    firstName = StringField('First Name', validators=[DataRequired(), Length(max=30)])
    lastName = StringField('Last Name', validators=[DataRequired(), Length(max=30)])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class SearchForm(FlaskForm):
    keyword = StringField('Search', validators=[DataRequired()])
    search_by = SelectField('Search By', choices=[('book', 'Book'),
                                                  ('author', 'Author'),
                                                  ('library', 'Library'),
                                                  ('genre', 'Genre')],
                            render_kw={'style': 'width: 9ch'})
    submit = SubmitField('Submit')
    lend = SubmitField('Lend This Book')


class ReturnBookForm(FlaskForm):
    submit = SubmitField('return This Book')









