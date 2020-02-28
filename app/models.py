from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Musician(db.Model):
    __table__ = db.Model.metadata.tables['Musician']


class Venue(db.Model):
    __table__ = db.Model.metadata.tables['Venue']


class Administrator(db.Model):
    __table__ = db.Model.metadata.tables['Administrator']


class Profile(db.Model):
    __table__ = db.Model.metadata.tables['Profile']

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
