from datetime import timedelta

from flask import Blueprint, render_template, request, session, redirect, flash, url_for
from forms import LoginForm, RegisterForm, PasswordResetForm
from flask_limiter import Limiter
from flask_bcrypt import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature


report_system = Blueprint("report_system", __name__)

@report_system.record_once
def record_params(setup_state):
    app = setup_state.app
    app.config['SESSION_COOKIE_NAME'] = "staff details"
    app.config['SESSION_LIFETIME'] = timedelta(weeks=2)
    global serializer
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@report_system.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if form.validate_on_submit():
                session.clear()
                session['email'] = form.email.data
                flash("You logged in successfully", "success")
                return redirect(url_for('map.main_map_page'))
    return render_template('login.html', form=form)

@report_system.route('/register',  methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        pass
    return render_template('register.html', form=form)

@report_system.route('/password_reset',  methods=['GET', 'POST'])
def password_reset():
    form = PasswordResetForm()
    if form.validate_on_submit():
        pass
    return render_template('password_reset.html', form=form)

@report_system.route('/logout')
def logout():
    session.clear()
    flash("You logged out successfully", "success")
    return redirect(url_for('map.main_map_page'))