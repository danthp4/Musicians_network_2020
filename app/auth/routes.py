from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response, abort
from app.auth.forms import SignupForm, LoginForm
from app.models import Profile, Musician, Venue
from app import db, login_manager
from flask_login import login_required, login_user, logout_user, current_user
from datetime import timedelta
from urllib.parse import urlparse, urljoin

from sqlalchemy.exc import IntegrityError

bp_auth = Blueprint('auth', __name__)

def is_safe_url(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc 

def get_safe_redirect():
    url = request.args.get('next')
    if url and is_safe_url(url):
        return url
    url = request.referrer
    if url and is_safe_url(url):
        return url
    return '/'

@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return Profile.query.get(user_id)
    return None

@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth.login'))

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are logged in')
        return redirect(url_for('main.index'))
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        user = Profile.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email/password combination', 'error')
            return redirect(url_for('auth.login'))
        login_user(user)
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        profiles = Profile.query.filter(Profile.username != current_user.username).all()
        return redirect(next or url_for('main.index'))
    return render_template('login.html', form=form)

@bp_auth.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp_auth.route('/register/', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        flash('You are logged in')
        return redirect(url_for('main.index'))
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Profile(username=form.username.data, email=form.email.data, profile_name=None,
                        profile_description=None, profile_image=None, location=None, rating=None)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            response = make_response(redirect(url_for('main.index')))
            response.set_cookie("username", form.username.data)
            user = Profile.query.filter_by(email=form.email.data).first()
            login_user(user)
            if form.option.data == 'm':
                user = Musician(gender=None, profile_id = current_user.profile_id,
                                birthdate=None, availability=None, sc_id=None)
                db.session.add(user)
            else:
                user = Venue(venue_capacity=None, profile_id = current_user.profile_id,
                                venue_type=None)
                db.session.add(user)
            db.session.commit()
            return response
        except IntegrityError:
            db.session.rollback()
            flash('Unable to register {}. Please try again.'.format(form.username.data), 'error')
    return render_template('register.html', form=form)

    # function that returns account type (musician/venue)
    def account_type(user_id):
        musician = Musician.query.filter_by(profile_id=user_id).first()
        venue = Venue.query.filter_by(profile_id=user_id).first()
        if musician is not None and venue is None:
            return print('musician')
        elif venue is not None and musician is None:
            return print('venue')
        else:
            return print('not found')