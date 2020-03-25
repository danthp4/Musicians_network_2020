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
    __tablename__ = "Administrator"
    admin_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    admin_name = db.Column(db.Text, nullable= False)
    profile_id = db.Column(db.Integer, db.ForeignKey('Profile.profile_id'), nullable=False)


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

    __mapper__args__ = {"polymorphic_identity": "profile"}

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


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    user_type = db.Column(db.String(10), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": user_type
    }

    def __repr__(self):
        return '<User Email: {}, Name: {}>'.format(self.email, self.name)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Student(User):
    __tablename__ = 'student'
    id = db.Column(None, db.ForeignKey('user.id'), primary_key=True)
    student_ref = db.Column(db.Integer)
    grades = db.relationship('Grade', backref='students')

    __mapper_args__ = {"polymorphic_identity": "student"}

    def __repr__(self):
        return '<Student ID: {}, name: {}>'.format(self.student_ref, self.name)


class Teacher(User):
    __tablename__ = 'teacher'
    id = db.Column(None, db.ForeignKey('user.id'), primary_key=True)
    teacher_ref = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text)
    courses = db.relationship('Course', backref='teachers')

    __mapper_args__ = {"polymorphic_identity": "teacher"}

    def __repr__(self):
        return '<Teacher ID: {}, Title: {}, Name: {}.>'.format(self.teacher_ref, self.title, self.name)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id), nullable=False)
    grades = db.relationship('Grade', backref='courses')

    def __repr__(self):
        return '<Course code: {}, name: {}>'.format(self.code, self.name)


class Grade(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey(Course.id), nullable=False, primary_key=True)
    grade = db.Column(db.Text)

    def __repr__(self):
        return '<Grade {}>'.format(self.grade)
