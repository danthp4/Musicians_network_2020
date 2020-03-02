from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.forms import SignupForm, LoginForm
from app.models import Profile
from app import db
from sqlalchemy.exc import IntegrityError

bp_main = Blueprint('main', __name__)


@bp_main.route('/')
def index():
    return render_template('index.html')


@bp_main.route('/userprofile/')
def signed_in_index():
    return render_template('index_after_login.html')


@bp_main.route('/register/', methods=['POST', 'GET'])
def register():
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Profile(username=form.username.data, email=form.email.data, profile_name=None,
                        profile_description=None, genre_id=None, profile_url=None, location=None, rating=None)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.signed_in_index'))
        except IntegrityError:
            db.session.rollback()
            flash('Unable to register {}. Please try again.'.format(form.username.data), 'error')
    return render_template('register.html', form=form)


@bp_main.route('/login/', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        conn = db.make_connector()
        email = form.email.data
        password = form.password.data

        user = Profile.query.filter_by(email=email).first()
        if user:
            if user.check_password(password=password):
                # login_user(user)
                # next = request.args.get('next')
                return redirect(url_for('main.signed_in_index'))
        # no email found
        flash('Invalid username/password combination', 'error')
    return render_template('login.html', form=form)


