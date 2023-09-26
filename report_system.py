from datetime import timedelta
from os import getenv

from flask import Blueprint, render_template, request, session, redirect, flash, url_for
from flask_mail import Mail, Message
from forms import LoginForm, RegisterForm, PasswordResetForm
from flask_bcrypt import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

report_system = Blueprint("report_system", __name__)

malvern_maps_cluster = MongoClient(getenv("MONGODB_URL"))
malvern_maps_db = malvern_maps_cluster["malvern_maps"]

@report_system.record_once
def record_params(setup_state):
    global serializer, mail
    app = setup_state.app
    app.config['SESSION_COOKIE_NAME'] = "staff details"
    app.config['SESSION_LIFETIME'] = timedelta(weeks=2)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'malvern.maps.verify@gmail.com'
    app.config['MAIL_PASSWORD'] = getenv("GMAIL_APP_PASSWORD")
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    print("recorded params")

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

def save_staff_in_database(email, password):
    malvern_maps_db["registered-accounts"].insert_one({"email": email, "password": password, "verified": False})

def send_verification_email(email, token):
    msg = Message(
        subject='Email verification',
        sender='Malvern Maps',
        recipients=[email]
    )
    msg.body = f"""Thank you for registering. Please click on the following link to verify your email address:"""
        #{url_for('report_system.verify_email', token=token, _external=True)}"""
    mail.send(msg)

@report_system.route('/register',  methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        email, password = form.email.data, form.password.data
        verification_token = serializer.dumps(email, salt='email-confirm')

        save_staff_in_database(email, generate_password_hash(password).decode('utf-8'))
        send_verification_email(email, verification_token)

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