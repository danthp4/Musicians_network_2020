from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, TextAreaField, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo


class ProfileForm(FlaskForm):
    description = TextAreaField('Profile description', validators=[DataRequired()])
    profile_name = StringField('Profile Name', validators=[DataRequired()])
    location = SelectField(u'City', choices=[('London', 'London'), ('Machester', 'Manchester'), ('Berlin', 'Berlin')])
    genre = SelectMultipleField(label='Genre', choices=[('1', 'Rock'), ('2', 'Drum and Bass'), ('3', 'Techno'),
                                                        ('4', 'Funk'), ('5', 'Disco'), ('6', 'Metal'),
                                                        ('7', 'Hip-Hop'), ('8', 'Indie')], validators=[DataRequired()])
    submit = SubmitField('Save')

class SettingsForm(FlaskForm):
    username = StringField('New Username', validators=[DataRequired()])
    email = StringField('New Email address', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat New Password')
    submit = SubmitField('Save')
