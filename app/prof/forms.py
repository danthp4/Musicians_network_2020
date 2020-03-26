from app import images
from app.models import Profile
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField, StringField, SelectField, TextAreaField, SelectMultipleField, PasswordField, DateField, \
    IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class ProfileForm(FlaskForm):
    description = TextAreaField('Profile description')
    profile_name = StringField('Profile Name', validators=[DataRequired()])
    location = SelectField(u'City', choices=[('London', 'London'), ('Machester', 'Manchester'), ('Berlin', 'Berlin')])
    genre = SelectMultipleField(label='Genre', choices=[('1', 'Rock'), ('2', 'Drum and Bass'), ('3', 'Techno'),
                                                        ('4', 'Funk'), ('5', 'Disco'), ('6', 'Metal'),
                                                        ('7', 'Hip-Hop'), ('8', 'Indie')], validators=[DataRequired()])
    profile_image = FileField('Profile Image', validators=[FileAllowed(images, 'Images only')])
    submit = SubmitField('Save')


class MusicianForm(FlaskForm):
    gender = SelectField(u'Gender', choices=[('1', 'Male'), ('0', 'Female')], validators=[DataRequired()])
    birthdate = DateField('Birthdate', format='%Y/%m/%d')
    availability = SelectField(u'Availability', choices=[('1', 'Available'), ('0', 'Unavailable')],
                               validators=[DataRequired()])
    sc_id = StringField('Soundcloud User ID')


class VenueForm(FlaskForm):
    capacity = IntegerField('Venue Capacity')
    venue_type = StringField('Venue Type')
    # user can enter image file and/or embed youtube link
    venue_image = FileField('Image', validators=[FileAllowed(images, 'Images only')])
    youtube = StringField('YouTube Embed ID')


class SettingsForm(FlaskForm):
    username = StringField('New Username', validators=[DataRequired()])
    email = StringField('New Email address', validators=[DataRequired(), Email()])
    password = PasswordField('New Password',
                             validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat New Password')
    submit = SubmitField('Save')

    def validate_username(self, username):
        user = Profile.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('An account is already registered for that username.')

    def validate_email(self, email):
        user = Profile.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('An account is already registered for that email.')


class RatingForm(FlaskForm):
    rating = SelectField(u'Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    submit = SubmitField('Rate!')
