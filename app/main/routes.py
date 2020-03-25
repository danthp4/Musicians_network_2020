from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Profile, Profile_Genre, Genre, Musician, Venue
from app import db, login_manager
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

bp_main = Blueprint('main', __name__)
bp_about = Blueprint('about', __name__, url_prefix='/about')

@bp_main.route('/')
def index():
    if current_user.is_authenticated:
        # show musicians only
        profiles = Profile.query.join(Musician).filter(Musician.profile_id != current_user.profile_id).all()
        relations = Profile_Genre.query.filter(Profile_Genre.profile_id != current_user.profile_id).all()
        genres = Genre.query.all()
        return render_template('home.html', profiles=profiles, relations=relations, genres=genres)
    else:
        return render_template('index.html')

@bp_main.route('/venues')
@login_required
def venues():
    profiles = Profile.query.join(Venue).filter(Venue.profile_id != current_user.profile_id).all()
    relations = Profile_Genre.query.filter(Profile_Genre.profile_id != current_user.profile_id).all()
    genres = Genre.query.all()
    return render_template('venues.html', profiles=profiles, relations=relations, genres=genres)

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

@bp_main.route('/soundcloud_id')
def soundcloud_id():
    return render_template('soundcloud_id.html')