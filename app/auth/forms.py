from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, RadioField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from app.models import Profile


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    option = RadioField('Account Type', choices=[('m','Musician'),('v','Venue')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Profile.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('An account is already registered for that username.')
    
    def validate_email(self, email):
        user = Profile.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('An account is already registered for that email.')


class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
