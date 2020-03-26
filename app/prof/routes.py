from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.prof.forms import images, ProfileForm, SettingsForm, MusicianForm, VenueForm
from app.models import Profile, Profile_Genre, Genre, Musician, Venue, Media
from app import db, login_manager
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

bp_prof = Blueprint('prof', __name__)

@bp_prof.route('/profile/<username>')
@login_required
def profile(username):
    user = Profile.query.filter_by(username=username).first()
    if user is not None:
        relations = Profile_Genre.query.filter(Profile_Genre.profile_id != current_user.profile_id).all()
        genres = Genre.query.join(Profile_Genre).join(Profile).filter_by(username=username).with_entities(Genre.genre_name)
        # check if it's musician
        musician = Musician.query.filter_by(profile_id=user.profile_id).first()
        venue = Venue.query.filter_by(profile_id=user.profile_id).first()
        if musician is not None:
            return render_template('musicians_profile.html', user=user, genres=genres, musician=musician)
        elif venue is not None:
            return render_template('venue_profile.html', user=user, genres=genres)
        else:
            flash('User {} is not properly registered.'.format(username))
            return redirect(url_for('main.index'))
    else:
        flash('User with username {} is not found.'.format(username))
        return redirect(url_for('main.index'))


@bp_prof.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    user = Profile.query.filter_by(profile_id=current_user.profile_id).first()
    # displays default input
    form.profile_name.data = user.profile_name
    form.description.data = user.profile_description
    form.location.data = user.location

    musician = Musician.query.filter_by(profile_id=user.profile_id).first()
    venue = Venue.query.filter_by(profile_id=user.profile_id).first()
    if musician is not None:
        adaptive_form = MusicianForm()
        adaptive_form.birthdate.data = musician.birthdate
        adaptive_form.sc_id.data = musician.sc_id
        account = 'musician'
    elif venue is not None:
        adaptive_form = VenueForm()
        adaptive_form.capacity.data = venue.venue_capacity
        adaptive_form.venue_type.data = venue.venue_type
        account = 'venue'
    else:
        flash('User with username is not registered properly.')
        return redirect(url_for('main.index')) 

    if request.method == 'POST' and form.validate_on_submit():
        try:
            filename = images.save(request.files['profile_image'])
            url = images.url(filename)
            # Update user information
            user.profile_name = form.profile_name.data
            user.profile_description = form.description.data
            user.location = form.location.data
            user.profile_image = url
            # Delete existing record with current profile_id then update with new one
            Profile_Genre.query.filter_by(profile_id=current_user.profile_id).delete()
            # Iterate over chosen Genre and update Musician/Genre table
            genre_list = form.genre.data
            for genre in genre_list:
                relation = Profile_Genre(profile_id=current_user.profile_id, genre_id=int(genre))
                db.session.add(relation)
                db.session.commit()
            
            if musician is not None:
                musician.gender = int(adaptive_form.gender.data)
                musician.birthdate = adaptive_form.birthdate.data
                musician.availability = int(adaptive_form.availability.data)
                musician.sc_id = adaptive_form.sc_id.data
            elif venue is not None:
                venue.venue_capacity = adaptive_form.capacity.data
                venue.venue_type = adaptive_form.venue_type.data
                filename = images.save(request.files['venue_image'])
                url = images.url(filename)
                media = Media(venue_id=venue.venue_id, media_title=None, media_content=url)
                db.session.add(media)
            db.session.commit()
            return redirect(url_for('main.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Unable to update {}. Please try again.'.format(form.username.data), 'error')

    return render_template('edit_profile.html', form=form, account=account, account_form=adaptive_form)

# A place to edit personal information (username, email, password)
@bp_prof.route('/settings', methods=['POST', 'GET'])
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
    return render_template('settings.html', form=form)