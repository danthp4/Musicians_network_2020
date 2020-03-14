from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class Musician(db.Model):
    __table__ = db.Model.metadata.tables['Musician']


class Venue(db.Model):
    __table__ = db.Model.metadata.tables['Venue']
    
class Genre(db.Model):
    __table__ = db.Model.metadata.tables['Genre']

class Administrator(db.Model):
    __table__ = db.Model.metadata.tables['Administrator']

class Profile(UserMixin, db.Model):
    __tablename__ = "user"

    __table__ = db.Model.metadata.tables['Profile']

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # have to use primary key
    def get_id(self):
        return self.profile_id

class Profile_Genre(db.Model):
    __tablename__ = 'profile/genre'

    profile_id = db.Column(db.Integer, db.ForeignKey(Profile.profile_id), nullable=False, primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey(Genre.genre_id), nullable=False, primary_key=True)