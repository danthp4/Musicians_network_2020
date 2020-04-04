from app import db
from app.models import Profile, Profile_Genre, Genre, Musician, Venue, \
    Media, Administrator
from app.prof.forms import images, ProfileForm, SettingsForm, MusicianForm, \
    VenueForm
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

bp_prof = Blueprint('prof', __name__)


@bp_prof.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = Profile.query.filter_by(username=username).first()
    admin_users = Administrator.query.all()
    if user is not None and request.method == 'GET':
        admin = Administrator.query.join(Profile).filter(
            Administrator.profile_id == current_user.profile_id
            ).first()
        if user.block == 1 and admin is None:
            flash('User {} is blocked by Administrators'.format(username))
            return redirect(url_for('main.index', account='musicians'))
        relations = Profile_Genre.query.filter(Profile_Genre.profile_id !=
                                               current_user.profile_id).all()
        genres = Genre.query.join(
                 Profile_Genre).join(
                 Profile).filter_by(
                    username=username).with_entities(Genre.genre_name)
        # check account type
        musician = Musician.query.filter_by(profile_id=user.profile_id).first()
        venue = Venue.query.filter_by(profile_id=user.profile_id).first()
        user_admin = Administrator.query.filter(
                     Administrator.profile_id == user.profile_id).first()
        if musician is not None:
            return render_template('musicians_profile.html', user=user,
                                   genres=genres, musician=musician,
                                   admin=user_admin)
        elif venue is not None:
            medias = Media.query.filter_by(venue_id=venue.venue_id).all()
            return render_template('venue_profile.html', user=user,
                                   genres=genres, venue=venue,
                                   medias=medias, admin=user_admin)
        else:
            flash('User {} is not properly registered.'.format(username))
            return redirect(url_for('main.index', account='musicians'))
    elif user is None:
        flash('User with username {} is not found.'.format(username))
        return redirect(url_for('main.index', account='musicians'))
    else:
        flash('Please search through main index.')
        return redirect(url_for('main.search'))


@bp_prof.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    user = Profile.query.filter_by(profile_id=current_user.profile_id).first()
    musician = Musician.query.filter_by(profile_id=user.profile_id).first()
    venue = Venue.query.filter_by(profile_id=user.profile_id).first()
    admin_users = Administrator.query.all()
    if musician is not None:
        adaptive_form = MusicianForm()
        account = 'musician'
    elif venue is not None:
        adaptive_form = VenueForm()
        account = 'venue'
    if request.method == 'GET':
        # displays default input
        form.profile_name.data = user.profile_name
        form.description.data = user.profile_description
        form.location.data = user.location
        if account == 'musician':
            adaptive_form.sc_id.data = musician.sc_id
        elif account == 'venue':
            adaptive_form.capacity.data = venue.venue_capacity
            adaptive_form.venue_type.data = venue.venue_type
        else:
            flash('User with username is not registered properly.')
            return redirect(url_for('main.index', account='musicians'))
        return render_template('edit_profile.html', form=form,
                               user_type=account,
                               account_form=adaptive_form, admins=admin_users)
    elif request.method == 'POST' and form.validate():
        try:
            # Update user information
            if form.profile_image.data is not None:
                if user.profile_image != '' and user.profile_image is not None:
                    import os
                    file_path = images.path(
                                os.path.basename(user.profile_image))
                    os.remove(file_path)
                filename = images.save(request.files['profile_image'])
                url = images.url(filename)
                user.profile_image = url
            user.profile_name = form.profile_name.data
            user.profile_description = form.description.data
            user.location = form.location.data
            if len(form.genre.data) != 0:
                # Delete existing record then update with new one
                Profile_Genre.query.filter_by(
                    profile_id=current_user.profile_id).delete()
                # Iterate over chosen Genre and update Musician/Genre table
                for genre in form.genre.data:
                    relation = Profile_Genre(
                               profile_id=current_user.profile_id,
                               genre_id=int(genre))
                    db.session.add(relation)
                    db.session.commit()

            if musician is not None:
                adaptive_form = MusicianForm()
                musician.gender = int(adaptive_form.gender.data)
                musician.birthdate = adaptive_form.birthdate.data
                musician.availability = int(adaptive_form.availability.data)
                musician.sc_id = adaptive_form.sc_id.data
            elif venue is not None:
                adaptive_form = VenueForm()
                venue.venue_capacity = adaptive_form.capacity.data
                venue.venue_type = adaptive_form.venue_type.data

                if adaptive_form.venue_image.data is not None:
                    if media_counter(Media, 'image', venue.venue_id) >= 1:
                        # delete image and replace
                        import os
                        venue_image = Media.query.filter_by(
                            venue_id=venue.venue_id,
                            media_type='image'
                            )
                        file_path = images.path(os.path.basename(
                            venue_image.first().media_content
                            ))
                        os.remove(file_path)
                        venue_image.delete()
                    filename = images.save(request.files['venue_image'])
                    url = images.url(filename)
                    media = Media(venue_id=venue.venue_id, media_type='image',
                                  media_content=url)
                    db.session.add(media)

                if adaptive_form.youtube.data != '':
                    if media_counter(Media, 'youtube', venue.venue_id) >= 1:
                        # delete youtube link and replace
                        Media.query.filter_by(venue_id=venue.venue_id,
                                              media_type='youtube').delete()
                    url = adaptive_form.youtube.data
                    # Now remove unnecessary characters from string
                    url = url.lstrip('https://www.youtube.com/ \
                                     watch?v ').split("&", 1)[0].lstrip('=')
                    media = Media(venue_id=venue.venue_id,
                                  media_type='youtube', media_content=url)
                    db.session.add(media)
            db.session.commit()
            return redirect(url_for('prof.profile', username=user.username))
        except IntegrityError:
            db.session.rollback()
            flash('Unable to update {}. \
                  Please try again.'.format(current_user.username), 'error')
    return render_template('edit_profile.html', form=form, user_type=account,
                           account_form=adaptive_form, admins=admin_users)


# A place to edit personal information (username, email, password)
@bp_prof.route('/settings', methods=['POST', 'GET'])
@login_required
def settings():
    form = SettingsForm()
    admin_users = Administrator.query.all()
    if request.method == 'POST' and form.validate():
        user = Profile.query.filter_by(profile_id=current_user.profile_id
                                       ).first()
        try:
            user.set_password(form.password.data)
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            return redirect(url_for('main.index', account='musicians'))
        except IntegrityError:
            flash('Unable to update {}. \
                  Please try again.'.format(form.username.data), 'error')
    return render_template('settings.html', form=form, admins=admin_users)


def media_counter(Media_table, media_type, venue_id):
    medias = Media_table.query.filter_by(venue_id=venue_id,
                                         media_type=media_type).all()
    count = 0
    for media in medias:
        count += 1
    return count
