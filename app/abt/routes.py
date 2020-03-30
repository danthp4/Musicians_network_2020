from flask import Blueprint, render_template


bp_about = Blueprint('about', __name__, url_prefix='/about')


@bp_about.route('/musicians')
def musicians():
    return render_template('about_musicians.html')


@bp_about.route('/bands')
def bands():
    return render_template('about_bands.html')


@bp_about.route('/venues')
def venues():
    return render_template('about_venues.html')