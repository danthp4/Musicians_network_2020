from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Profile
from app import db, login_manager
from flask_login import login_required, current_user

bp_main = Blueprint('main', __name__)


@bp_main.route('/')
def index():
    if current_user.is_authenticated:
        profiles = Profile.query.filter(Profile.username != current_user.username).all()
        return render_template('home.html', profiles=profiles)
    else:
        return render_template('index.html')



@bp_main.route('/search', methods=['POST', 'GET'])
@login_required
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
        return redirect(url_for('main.index'))


@bp_main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        choices = form.genre.data
        return "Selected options: {}".format(choices)
    return render_template('profile.html', form=form)

