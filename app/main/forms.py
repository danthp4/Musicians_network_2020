from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, TextAreaField, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo


class ProfileForm(FlaskForm):
    description = TextAreaField('Profile description', validators=[DataRequired()])
    profile_name = StringField('Profile Name', validators=[DataRequired()])
    location = SelectField(u'City', choices=[('ldn', 'London'), ('mnc', 'Manchester'), ('bln', 'Berlin')])
    genre = SelectMultipleField(label='Genre', choices=[('rck', 'Rock'), ('dnb', 'Drum and Bass'), ('tcn', 'Techno'),
                                                        ('fnk', 'Funk'), ('dco', 'Disco'), ('mtl', 'Metal'),
                                                        ('hip', 'Hip-Hop'), ('ind', 'Indie')])

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register')

    submit = SubmitField('Save & Submit')
