from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from app.auth.forms import SignupForm, LoginForm
from app.models import Profile
from app import db, login_manager
from flask_login import login_required, login_user, logout_user, current_user
from datetime import timedelta
from urllib.parse import urlparse, urljoin

from sqlalchemy.exc import IntegrityError

bp_auth = Blueprint('auth', __name__)

@bp_auth.route('/login/', methods=['GET', 'POST'])
def login():
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
        return redirect(next or url_for('main.home'))
    return render_template('login.html', form=form)

@bp_auth.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp_auth.route('/register/', methods=['POST', 'GET'])
def register():
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Profile(username=form.username.data, email=form.email.data, profile_name=None,
                        profile_description=None, genre_id=None, profile_url=None, location=None, rating=None)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            response = make_response(redirect(url_for('main.home')))
            response.set_cookie("name", form.name.data)
            return response
        except IntegrityError:
            db.session.rollback()
            flash('Unable to register {}. Please try again.'.format(form.username.data), 'error')
    return render_template('register.html', form=form)

@login_manager.user_loader
def load_user(username):
    """Check if user is logged-in on every page load."""
    if username is not None:
        return Profile.query.get(username)
    return None

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

@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth.login'))