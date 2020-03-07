from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.main.forms import ProfileForm
from app.models import Profile
from app import db
from sqlalchemy.exc import IntegrityError
from flask_login import login_required, login_user, logout_user, current_user


bp_main = Blueprint('main', __name__)

# landing page: accessible before logging in
@bp_main.route('/')
def index():
    return render_template('index.html')

# only accessible after logging in
@bp_main.route('/home')
def home():
    profiles = Profile.query.all()
    return render_template('home.html', profiles=profiles)

@bp_main.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        term = request.form['search_term']
        if term == "":
            return redirect('/')
        results = Profile.query.filter(Profile.username.contains(term)).all()
        if not results:
            flash("No students found with that name.")
            return redirect('/')
        return render_template('search_results.html', results=results)
    else:
        return redirect(url_for('main.home'))

@bp_main.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileForm()
    return render_template('profile.html', form=form)