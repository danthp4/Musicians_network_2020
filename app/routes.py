from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.forms import SignupForm, LoginForm

bp_main = Blueprint('main', __name__)


@bp_main.route('/')
def index():
    return render_template('index.html')


@bp_main.route('/register/', methods=['POST', 'GET'])
def register():
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        flash('Signup requested for {}'.format(form.last_name.data))
    # Code to add the student to the database goes here
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@bp_main.route('/login/', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # flash('Signup requested for {}'.format(form.last_name.data))
    # Code to add the student to the database goes here
        return redirect(url_for('main.index'))
    return render_template('login.html', form=form)
