from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.main.forms import ProfileForm, SettingsForm
from app.models import Profile, Profile_Genre, Genre
from app import db, login_manager
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

bp_main = Blueprint('main', __name__)
bp_about = Blueprint('about', __name__, url_prefix='/about')

@bp_main.route('/')
def index():
    if current_user.is_authenticated:
        profiles = Profile.query.filter(Profile.username != current_user.username).all()
        relations = Profile_Genre.query.filter(Profile_Genre.profile_id != current_user.profile_id).all()
        genres = Genre.query.all()
        return render_template('home.html', profiles=profiles, relations=relations, genres=genres)
    else:
        return render_template('index.html')

@bp_main.route('/<username>')
@login_required
def profile(username):
    user = Profile.query.filter_by(username=username).first()
    genres = Genre.query.join(Profile_Genre).join(Profile).filter_by(username=username).with_entities(Genre.genre_name)
    return render_template('view_profile.html', user=user, genres=genres)

@bp_main.route('/musician/<username>')
@login_required
def musician_profile(username):
    user = Profile.query.filter_by(username=username).first()
    genres = Genre.query.join(Profile_Genre).join(Profile).filter_by(username=username).with_entities(Genre.genre_name)
    return render_template('musicians_profile.html', user=user, genres=genres)

@bp_main.route('/venue/<username>')
@login_required
def venue_profile(username):
    user = Profile.query.filter_by(username=username).first()
    genres = Genre.query.join(Profile_Genre).join(Profile).filter_by(username=username).with_entities(Genre.genre_name)
    return render_template('venue_profile.html', user=user, genres=genres)

@bp_about.route('/musicians')
def musicians():
    return render_template('about_musicians.html')


@bp_about.route('/bands')
def bands():
    return render_template('about_bands.html')


@bp_about.route('/venues')
def venues():
    return render_template('about_venues.html')


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
            results = Profile.query.join(Profile_Genre).join(Genre).filter(Genre.genre_name.contains(term)).all()
            msg = 'with'

        if not results:
            flash('No user found {} that {}.'.format(msg, category))
            return render_template('search_results.html', results=results)
        return render_template('search_results.html', results=results)
    else:
        return redirect(url_for('main.index'))


@bp_main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if request.method == 'POST' and form.validate():
        user = Profile.query.filter_by(profile_id=current_user.profile_id).first()
        try:
            # Update user information
            user.profile_name = form.profile_name.data
            user.profile_description = form.description.data
            user.location = form.location.data
            user.sc_user_id = form.sc_user_id.data
            # Delete existing record with current profile_id then update with new one
            Profile_Genre.query.filter_by(profile_id=current_user.profile_id).delete()
            # Iterate over chosen Genre and update Musician/Genre table
            genre_list = form.genre.data
            for genre in genre_list:
                relation = Profile_Genre(profile_id=current_user.profile_id, genre_id=int(genre))
                db.session.add(relation)
                db.session.commit()
            return redirect(url_for('main.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Unable to update {}. Please try again.'.format(form.username.data), 'error')
    return render_template('edit_profile.html', form=form, search=search)

# A place to edit personal information (username, email, password)
@bp_main.route('/settings', methods=['POST', 'GET'])
@login_required
def settings():
    form = SettingsForm()
    if request.method == 'POST' and form.validate():
        user = Profile.query.filter_by(profile_id=current_user.profile_id).first()
        try:
            user.set_password(form.password.data)
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            return redirect(url_for('main.index'))
        except IntegrityError:
            flash('Unable to update {}. Please try again.'.format(form.username.data), 'error')
    return render_template('settings.html', form=form, search=search)


@bp_main.route('/soundcloud_id')
def soundcloud_id():
    return render_template('soundcloud_id.html')