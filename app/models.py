from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class Profile(UserMixin, db.Model):
    __tablename__ = "Profile"
    profile_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    profile_name = db.Column(db.Text)
    profile_description = db.Column(db.Text)
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text)
    rating = db.Column(db.REAL)
    profile_image = db.Column(db.VARCHAR)
    block = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<User Email: {}, Username: {}>'.format(self.email, self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.profile_id


class Musician(db.Model):
    __tablename__ = 'Musician'
    musician_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    gender = db.Column(db.Integer)
    profile_id = db.Column(db.Integer, db.ForeignKey('Profile.profile_id'), nullable=False)
    birthdate = db.Column(db.Text)
    availability = db.Column(db.Integer)
    sc_id = db.Column(db.Integer)
    profile = db.relationship('Profile', backref='Musician')

    def __repr__(self):
        return '<Availability: {}>'.format(self.availability)


class Venue(db.Model):
    __tablename__ = 'Venue'
    venue_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    venue_capacity = db.Column(db.Integer)
    profile_id = db.Column(db.Integer, db.ForeignKey('Profile.profile_id'), nullable=False)
    venue_type = db.Column(db.Text)
    profile = db.relationship('Profile', backref='Venue')

    def __repr__(self):
        return '<Venue Capacity:{}, Venue Type: {}>'.format(self.venue_capacity, self.venue_type)


class Genre(db.Model):
    __tablename__ = 'Genre'
    genre_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    genre_name = db.Column(db.Text)

    def __repr__(self):
        return '<Genre ID:{}, Genre Name: {}>'.format(self.genre_id, self.genre_name)


class Media(db.Model):
    __tablename__ = 'Media'
    media_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.venue_id'), nullable=False)
    media_type = db.Column(db.Text, nullable=False)
    media_content = db.Column(db.VARCHAR)


class Administrator(db.Model):
    __tablename__ = "Administrator"
    admin_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('Profile.profile_id'), nullable=False)


class Profile_Genre(db.Model):
    __tablename__ = 'profile/genre'
    profile_id = db.Column(db.Integer, db.ForeignKey(Profile.profile_id), nullable=False, primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey(Genre.genre_id), nullable=False, primary_key=True)

