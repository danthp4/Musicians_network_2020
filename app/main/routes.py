from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.main.forms import ProfileForm, SettingsForm
from app.models import Profile
from app import db, login_manager
from flask_login import login_required, current_user

bp_main = Blueprint('main', __name__)


@bp_main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        profiles = Profile.query.filter(Profile.username != current_user.username).all()
        return render_template('home.html', profiles=profiles, search=search)
    else:
        return render_template('index.html', search=search)

@bp_main.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    if request.method == 'POST':
        term = request.form['search_term']
        category = request.form['category']
        if term == "":
            return redirect('/')
        elif category == 'Name':
            results = Profile.query.filter(Profile.username.contains(term)).all()
            msg = 'with'
        elif category == 'Location':
            results = Profile.query.filter(Profile.location.contains(term)).all()
            msg = 'in'
        elif category == 'Genre':
            results = Profile.query.filter(Profile.genre.contains(term)).all()
            msg = 'with'

        if not results:
            flash('No user found {} that {}.'.format(msg, category))
        return render_template('search_results.html', results=results)
    else:
        return redirect(url_for('main.index'))


@bp_main.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if request.method == 'POST' and form.validate():
        user = Profile.query.filter_by(profile_id=current_user.profile_id).first()
        # conn.execute(user.update().values(profile_name=form.profile_name.data))
        user.profile_name = form.profile_name.data
        user.profile_description = form.description.data
        user.genre_id = form.genre.data
        user.location = form.location.data
        db.session.commit()
        choices = form.genre.data
        return redirect(url_for('main.index'))
    return render_template('edit_profile.html', form=form, search=search)

# A place to edit personal information (username, email, password)
@bp_main.route('/settings', methods=['POST', 'GET'])
@login_required
def settings():
    form = SettingsForm()
    if request.method == 'POST' and form.validate():
        user = Profile.query.filter_by(profile_id=current_user.profile_id).first()
        user.set_password(form.password.data)
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('settings.html', form=form, search=search)


