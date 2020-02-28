from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.auth.forms import SignupForm, LoginForm
from app.models import Profile
from app import db
from sqlalchemy.exc import IntegrityError

bp_main = Blueprint('main', __name__)


@bp_main.route('/')
def landing():
    return render_template('landing.html')

@bp_main.route('/home')
def index():
    return render_template('index.html')
