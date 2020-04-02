from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Profile, Profile_Genre, Genre, Musician, Venue, Administrator, Media, Profile_Rate

bp_main = Blueprint('main', __name__)


@bp_main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        admin = Administrator.query.join(Profile).filter_by(profile_id=current_user.profile_id).first()
        relations = Profile_Genre.query.filter(Profile_Genre.profile_id != current_user.profile_id).all()
        genres = Genre.query.all()
        admin_users = Administrator.query.all()
        # show non-blocked musicians for users and all users for admins
        block_filter = 0 if admin is None else 1
        account = request.args.get('account')
        if account != 'venues':
            profiles = Profile.query.join(Musician).filter(Musician.profile_id != current_user.profile_id
                                                           , Profile.block <= block_filter).with_entities(
                Profile.username,
                Profile.location,
                Profile.profile_id,
                Profile.rating,
                Musician.sc_id,
                Profile.profile_description,
                Profile.block, Profile.profile_image)
            return render_template('home.html', profiles=profiles, relations=relations, genres=genres,
                                   admins=admin_users)
        else:
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
            media = Media.query.join(Venue).filter(Venue.profile_id != current_user.profile_id).all()
            return render_template('venues.html', profiles=profiles, relations=relations,
                                   genres=genres, media=media, admins=admin_users)
    else:
        return render_template('index.html')


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
        else:
            admin = Administrator.query.join(Profile).filter_by(profile_id=current_user.profile_id).first()
            block_filter = 0 if admin is None else 1

            if search_type == 'Artists':
                media = None
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
            
            try:
                results[0].username
            except:
                flash('No user found {} that {}.'.format(msg, category))
                return render_template('search_results.html', results=results, term=term, relations=relations,
                                       genres=genres, search_type=search_type, media=media)
            return render_template('search_results.html', results=results, term=term, relations=relations,
                                   genres=genres, search_type=search_type, media=media)
    else:
        return redirect(url_for('main.index', account='musicians'))


@bp_main.route('/block')
@login_required
def block():
    username = request.args.get('username')
    admin = Administrator.query.join(Profile).filter(Administrator.profile_id ==
                                                     current_user.profile_id).first()
    if admin is not None:
        try:
            user = Profile.query.filter_by(username=username).first()
            if user.block == 0:
                user.block = 1
                flash("Account {} is successfully blocked.".format(username))
            else:
                user.block = 0
                flash("Account {} is successfully unblocked.".format(username))
            db.session.commit()
        except:
            flash("Invalid Command. Please block through user's card", 'error')

    else:
        flash("You are not authorised to remove users from Musician's Network. Please contact Administrators")
    return redirect(url_for('main.index', account='musicians'))


@bp_main.route('/rate')
@login_required
def rate():
    username = request.args.get('username')
    rate_value = request.args.get('rate_value')
    if username == current_user.username:
        flash('You are unable to rate yourself.')
        return redirect(url_for('main.index', account='musicians'))
    else:
        try:
            target_user = Profile.query.filter_by(username=username).first()
            relation = Profile_Rate.query.filter_by(target_id=target_user.profile_id,
                                                    profile_id=current_user.profile_id).first()
            # if current_user has never rated target_user
            if relation is None:
                rating = Profile_Rate(profile_id=current_user.profile_id, target_id=target_user.profile_id,
                                      rate=int(rate_value))
                db.session.add(rating)
            else:
                relation.rate = int(rate_value)
            db.session.commit()

            # calculate target_user's new rating by averaging
            ratings = Profile_Rate.query.filter_by(target_id=target_user.profile_id).all()
            total_rate, n_rates = 0, 0
            for record in ratings:
                total_rate += record.rate
                n_rates += 1
            target_user.rating = total_rate / n_rates
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Unable to rate {}. Please try again.'.format(target_user.username), 'error')
        return redirect(url_for('main.index', account='musicians'))


@bp_main.route('/blocked')
@login_required
def blocked():
    admin = Administrator.query.join(Profile).filter(Administrator.profile_id ==
                                                     current_user.profile_id).first()
    if admin is not None:
        account = request.args.get('account')
        relations = Profile_Genre.query.filter(Profile_Genre.profile_id != current_user.profile_id).all()
        genres = Genre.query.all()
        admin_users = Administrator.query.all()
        term = 'Blocked'
        if account == 'musicians':
            media = None
            blocked_users = Profile.query.join(Musician).filter(Musician.profile_id != current_user.profile_id
                                                                , Profile.block == 1).with_entities(
                Profile.username,
                Profile.location,
                Profile.profile_id,
                Profile.rating,
                Musician.sc_id,
                Profile.profile_description,
                Profile.block)
            return render_template('search_results.html', results=blocked_users, term=term, relations=relations,
                                   genres=genres, search_type='Artists',
                                   media=media, admins=admin_users)
        elif account == 'venues':
            blocked_users = Profile.query.join(Venue).filter(Venue.profile_id != current_user.profile_id,
                                                             Profile.block == 1).with_entities(
                Venue.venue_capacity,
                Profile.username,
                Profile.location,
                Profile.rating,
                Profile.profile_description,
                Profile.profile_id,
                Venue.venue_type, Profile.block,
                Venue.venue_id,
                Profile.profile_image)
            media = Media.query.join(Venue).filter(Venue.profile_id != current_user.profile_id).all()
            return render_template('search_results.html', results=blocked_users, term=term, relations=relations,
                                   genres=genres, search_type='Venues',
                                   media=media, admins=admin_users)
        else:
            flash("Invalid request.", 'error')
            return redirect(url_for('main.index', account='musicians'))
    else:
        flash("You are not authorised to view blocked users from Musician's Network.")
        return redirect(url_for('main.index', account='musicians'))


@bp_main.route('/ratings')
@login_required
def ratings():
    account = request.args.get('account')
    upper, lower = rate_range_calculator(int(request.args.get('star')))
    relations = Profile_Genre.query.filter(Profile_Genre.profile_id != current_user.profile_id).all()
    genres = Genre.query.all()
    admin_users = Administrator.query.all()
    term = 'Rating'
    if account == 'musicians':
        media = None
        results = Profile.query.join(Musician).filter(Musician.profile_id != current_user.profile_id
                                                      , Profile.block == 0, Profile.rating > lower,
                                                      Profile.rating <= upper).order_by(desc(Profile.rating)). \
            with_entities(Profile.username,
                          Profile.location,
                          Profile.profile_id,
                          Profile.rating,
                          Musician.sc_id,
                          Profile.profile_description,
                          Profile.block)
        return render_template('search_results.html', results=results, term=term, relations=relations,
                               genres=genres, search_type='Artists',
                               media=media, admins=admin_users)
    elif account == 'venues':
        results = Profile.query.join(Venue).filter(Venue.profile_id != current_user.profile_id,
                                                   Profile.block == 0, Profile.rating > lower,
                                                   Profile.rating <= upper).order_by(Profile.rating). \
            with_entities(Venue.venue_capacity,
                          Profile.username,
                          Profile.location,
                          Profile.rating,
                          Profile.profile_description,
                          Profile.profile_id,
                          Venue.venue_type, Profile.block,
                          Venue.venue_id,
                          Profile.profile_image)
        media = Media.query.join(Venue).filter(Venue.profile_id != current_user.profile_id).all()
        return render_template('search_results.html', results=results, term=term, relations=relations,
                               genres=genres, search_type='Venues',
                               media=media, admins=admin_users)
    else:
        flash("Invalid request.", 'error')
        return redirect(url_for('main.index', account='musicians'))


def rate_range_calculator(star):
    maximum = star + 0.5
    minimum = star - 0.5
    if star == 0:
        maximum = 5
    return maximum, minimum
