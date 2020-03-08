<<<<<<< HEAD
from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from app.auth.forms import SignupForm, LoginForm
=======
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.main.forms import ProfileForm
>>>>>>> Dan
from app.models import Profile
from app import db
from sqlalchemy.exc import IntegrityError
from flask_login import login_required, login_user, logout_user, current_user


bp_main = Blueprint('main', __name__)

@bp_main.route('/')
def index():
    if current_user.is_anonymous:
        return render_template('index.html')
    else:
        profiles = Profile.query.filter(Profile.username != current_user.username).all()
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
<<<<<<< HEAD
        return redirect(url_for('main.index')) 
=======
        return redirect(url_for('main.home'))

@bp_main.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileForm()
    return render_template('profile.html', form=form)
>>>>>>> Dan
