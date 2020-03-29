from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Profile, Profile_Genre, Genre, Musician, Venue, Administrator, Media
from app.prof.forms import RatingForm

bp_main = Blueprint('main', __name__)
bp_about = Blueprint('about', __name__, url_prefix='/about')


@bp_main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        admin = Administrator.query.join(Profile).filter_by(profile_id=current_user.profile_id).first()
        form = RatingForm()
        # show non-blocked musicians for users and all users for admins
        if admin is None:
            block_filter = 0
        else:
            block_filter = 1
        profiles = Profile.query.join(Musician).filter(Musician.profile_id != current_user.profile_id
                                                        , Profile.block <= block_filter).with_entities(
                                                                                    Profile.username,
                                                                                    Profile.location,
                                                                                    Profile.profile_id,
                                                                                    Profile.rating,
                                                                                    Musician.sc_id,
                                                                                    Profile.profile_description,
                                                                                    Profile.block)
        relations = Profile_Genre.query.filter(Profile_Genre.profile_id != current_user.profile_id).all()
        genres = Genre.query.all()
        admin_users = Administrator.query.filter(Administrator.profile_id != current_user.profile_id).all()

        user = Profile.query.filter_by(profile_id=current_user.profile_id).first()
        form.rating.data = user.rating
        if request.method == 'POST' and form.validate():
            user = Profile.query.filter_by(profile_id=current_user.profile_id).first()
            try:
                user.rating(form.rating.data)
                db.session.commit()
            except IntegrityError:
                flash('error')

        return render_template('home.html', profiles=profiles, relations=relations, genres=genres, 
                                            form=form, admin=admin_users)
    else:
        return render_template('index.html')


@bp_main.route('/venues', methods=['GET', 'POST'])
@login_required
def venues():
    admin = Administrator.query.join(Profile).filter_by(profile_id=current_user.profile_id).first()
    if admin is None:
        block_filter = 0
    else:
        block_filter = 1
    profiles = Profile.query.join(Venue).filter(Venue.profile_id != current_user.profile_id,
                                                Profile.block <= block_filter).with_entities(
                                                                                Venue.venue_capacity,
                                                                                Profile.username,
                                                                                Profile.location,
                                                                                Profile.rating,
                                                                                Profile.profile_description,
                                                                                Profile.profile_id,
                                                                                Venue.venue_type, Profile.block,
                                                                                Venue.venue_id,
                                                                                Profile.profile_image)

    relations = Profile_Genre.query.filter(Profile_Genre.profile_id != current_user.profile_id).all()
    genres = Genre.query.all()
    media = Media.query.join(Venue).filter(Venue.profile_id != current_user.profile_id).all()
    form = RatingForm()
    user = Profile.query.filter_by(profile_id=current_user.profile_id).first()
    form.rating.data = user.rating
    if request.method == 'POST' and form.validate():
        user = Profile.query.filter_by(profile_id=current_user.profile_id).first()
        try:
            user.rating(form.rating.data)
            db.session.commit()
        except IntegrityError:
            flash('error')

    return render_template('venues.html', profiles=profiles, relations=relations, genres=genres, form=form, media=media)


@bp_about.route('/musicians')
def musicians():
    return render_template('about_musicians.html')


@bp_about.route('/bands')
def bands():
    return render_template('about_bands.html')


@bp_about.route('/venues')
def venues():
    return render_template('about_venues.html')


@bp_main.route('/soundcloud_id')
def soundcloud_id():
    return render_template('soundcloud_id.html')


@bp_main.route('/youtube_id')
def youtube_id():
    return render_template('youtube_id.html')


@bp_main.route('/search', methods=['POST', 'GET'])
@login_required
def search_results():
    if request.method == 'POST':
        term, category = request.form['search_term'], request.form['category']
        search_type = request.form['search_type']

        relations = Profile_Genre.query.filter(Profile_Genre.profile_id != current_user.profile_id).all()
        genres = Genre.query.all()
        if term == "":
            return redirect('/')
        elif not Profile.query.join(Musician).filter(Profile.username.contains(term), Profile.block == 0):
            flash('No user found {} that {}.'.format(msg, category))
            return render_template('search_results.html', results=results)
        else:
            admin = Administrator.query.join(Profile).filter_by(profile_id=current_user.profile_id).first()
            if admin is None:
                block_filter = 0
            else:
                block_filter = 1
            
            if search_type == 'Artists':
                if category == 'Name':
                    results = Profile.query.join(Musician).filter(Profile.username.contains(term)
                                                        , Profile.block <= block_filter).with_entities(
                                                                                        Profile.username,
                                                                                        Profile.location,
                                                                                        Profile.profile_id,
                                                                                        Profile.rating,
                                                                                        Musician.sc_id,
                                                                                        Profile.profile_description,
                                                                                        Profile.block)
                    msg = 'with'
                elif category == 'Location':
                    results = Profile.query.join(Musician).filter(Profile.location.contains(term)
                                            , Profile.block <= block_filter).with_entities(
                                                                                Profile.username,
                                                                                Profile.location,
                                                                                Profile.profile_id,
                                                                                Profile.rating,
                                                                                Musician.sc_id,
                                                                                Profile.profile_description,
                                                                                Profile.block)
                    msg = 'in'
                elif category == 'Genre':
                    results = Profile.query.join(Profile_Genre).join(Genre).join(Musician).filter(
                                    Genre.genre_name.contains(term), Profile.block <= block_filter
                                                                ).with_entities(Profile.username,
                                                                                Profile.location,
                                                                                Profile.profile_id,
                                                                                Profile.rating,
                                                                                Musician.sc_id,
                                                                                Profile.profile_description,
                                                                                Profile.block)
                    msg = 'with'
            else:
                media = Media.query.join(Venue).filter(Venue.profile_id != current_user.profile_id).all()
                if category == 'Name':
                    results = Profile.query.join(Venue).filter(Profile.username.contains(term),
                                            Profile.block <= block_filter).with_entities(
                                                                            Venue.venue_capacity,
                                                                            Profile.username,
                                                                            Profile.location,
                                                                            Profile.rating,
                                                                            Profile.profile_description,
                                                                            Profile.profile_id,
                                                                            Venue.venue_type, Profile.block,
                                                                            Venue.venue_id,
                                                                            Profile.profile_image)
                    msg = 'with'
                elif category == 'Location':
                    results = Profile.query.join(Venue).filter(Profile.location.contains(term),
                                            Profile.block <= block_filter).with_entities(
                                                                            Venue.venue_capacity,
                                                                            Profile.username,
                                                                            Profile.location,
                                                                            Profile.rating,
                                                                            Profile.profile_description,
                                                                            Profile.profile_id,
                                                                            Venue.venue_type, Profile.block,
                                                                            Venue.venue_id,
                                                                            Profile.profile_image)
                    msg = 'in'
                elif category == 'Genre':
                    results = Profile.query.join(Profile_Genre).join(Genre).join(Venue).filter(
                                    Genre.genre_name.contains(term), Profile.block <= block_filter
                                                            ).with_entities(Venue.venue_capacity,
                                                                            Profile.username,
                                                                            Profile.location,
                                                                            Profile.rating,
                                                                            Profile.profile_description,
                                                                            Profile.profile_id,
                                                                            Venue.venue_type, Profile.block,
                                                                            Venue.venue_id,
                                                                            Profile.profile_image)
                    msg = 'with'
            return render_template('search_results.html', results=results, term=term, relations=relations, 
                                                            genres=genres, search_type=search_type, media=media)
    else:
        return redirect(url_for('main.index'))


@bp_main.route('/block/<username>')
@login_required
def block(username):
    admin = Administrator.query.join(Profile).filter(Administrator.profile_id ==
                                                     current_user.profile_id).first()
    if admin is not None:
        user = Profile.query.filter_by(username=username).first()
        if user.block == 0:
            user.block = 1
        else:
            user.block == 0
        db.session.commit()
        flash("Account {} is successfully blocked.".format(username))
    else:
        flash("You are not authorised to remove users from Musician's Network. Please contact Administrators")
    return redirect(url_for('main.index'))
