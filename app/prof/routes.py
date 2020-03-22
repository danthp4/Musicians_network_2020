from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.prof.forms import ProfileForm, SettingsForm
from app.models import Profile, Profile_Genre, Genre, Musician, Venue
from app import db, login_manager
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

bp_prof = Blueprint('prof', __name__)

@bp_prof.route('/profile/<username>')
@login_required
def profile(username):
    user = Profile.query.filter_by(username=username).first()
    genres = Genre.query.join(Profile_Genre).join(Profile).filter_by(username=username).with_entities(Genre.genre_name)
    # check if it's musician
    musician = Musician.query.filter_by(profile_id=user.profile_id).first()
    venue = Venue.query.filter_by(profile_id=user.profile_id).first()
    if musician:
        return render_template('musicians_profile.html', user=user, genres=genres)
    elif venue:
        return render_template('venue_profile.html', user=user, genres=genres)
    else:
        flash('User with username {} is not found.'.format(username))
        return render_template('view_profile.html', user=user, genres=genres)


@bp_prof.route('/edit_profile', methods=['GET', 'POST'])
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
    return render_template('edit_profile.html', form=form)

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