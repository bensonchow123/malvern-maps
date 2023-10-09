from datetime import timedelta
from os import getenv
from datetime import datetime

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
malvern_maps_db = malvern_maps_cluster["malvern-maps"]

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

def check_logged_in():
    if "email" in session:
        flash("logout in the sidebar to access this page", "danger")
        return True

def check_logged_out():
    if "email" not in session:
        flash("login in the sidebar to access this page", "danger")
        return True

@report_system.route('/login', methods=['GET', 'POST'])
def login():
    if check_logged_in():
        return redirect(url_for('map.main_map_page'))

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

def send_verification_email(email, url):
    msg = Message(
        subject='Email verification',
        sender=('Malvern Maps', 'malvern.maps.verify@gmail.com'),
        recipients=[email]
    )
    msg.body = (
        "Dear Staff Member,\n\n"
        "Thank you for using Malvern Maps! We have received a request for an action on your account. "
        "To proceed, please click on the following link:\n"
        f"{url}\n\n"
        "If you did not initiate this request, please disregard this email and rest assured that no changes will be made to your account.\n\n"
        "Best Regards,\n"
        "Benson Chow"
    )
    mail.send(msg)

@report_system.route('/register',  methods=['GET', 'POST'])
def register():
    if check_logged_in():
        return redirect(url_for('map.main_map_page'))

    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email, password = form.email.data, form.password.data
            verification_token = serializer.dumps(email, salt='email-verification')

            save_staff_in_database(email, generate_password_hash(password).decode('utf-8'))
            send_verification_email(
                email,
                url_for(
                    'report_system.verify_email',
                    token=verification_token,
                    _external=True
                )
            )
            flash("Please check your email to verify your account", "success")
            return redirect(url_for('report_system.login'))

    return render_template('register.html', form=form)

def verify_staff(email):
    malvern_maps_db["registered-accounts"].update_one({"email": email}, {"$set": {"verified": True}})

@report_system.route('/verify_email/<token>')
def verify_email(token):
    if check_logged_in():
        return redirect(url_for('map.main_map_page'))

    try:
        email = serializer.loads(token, salt='email-verification', max_age=7200)
        verify_staff(email)
        flash("Your email has been verified", "success")
        return redirect(url_for('report_system.login'))

    except SignatureExpired:
        flash("Your token is expired, please register your account again", "danger")
        return redirect(url_for('register'))

    except BadTimeSignature:
        flash("Your token is invalid, please register your account again", "danger")
        return redirect(url_for('register'))

@report_system.route('/password_reset',  methods=['GET', 'POST'])
def password_reset():
    if check_logged_in():
        return redirect(url_for('map.main_map_page'))

    form = PasswordResetForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            token = serializer.dumps([email, form.confirm_new_password.data], salt='password-reset')
            send_verification_email(
                email,
                url_for('report_system.verify_password_reset',
                        token=token,
                        _external=True
                        )
            )
            flash("Please check your email to verify the password reset attempt", "success")
            return redirect(url_for('report_system.login'))
    return render_template('password_reset.html', form=form)

def handle_changing_password(email, new_password):
    now = datetime.utcnow()

    malvern_maps_db['password-resets'].create_index("timestamp", expireAfterSeconds=2 * 24 * 60 * 60)  # 2 days in seconds
    malvern_maps_db["password-resets"].insert_one({"email": email, "timestamp": now})

    malvern_maps_db["registered-accounts"].update_one(
        {"email": email},
        {"$set": {"password": generate_password_hash(new_password).decode('utf-8')}}
    )

@report_system.route('/verify_password_reset/<token>', methods=['GET', 'POST'])
def verify_password_reset(token):
    if check_logged_in():
        return redirect(url_for('map.main_map_page'))

    try:
        password_reset_details = serializer.loads(token, salt='password-reset', max_age=3600)
        handle_changing_password(password_reset_details[0], password_reset_details[1])
        flash("Your password has been reset", "success")
        return redirect(url_for('report_system.login'))

    except SignatureExpired:
        flash("Your token is expired, please reset your password again", "danger")
        return redirect(url_for('password_reset'))

    except BadTimeSignature:
        flash("Your token is invalid, please reset your password again", "danger")
        return redirect(url_for('password_reset'))

@report_system.route('/logout')
def logout():
    if check_logged_out():
        return redirect(url_for('map.main_map_page'))

    session.clear()
    flash("You logged out successfully", "success")
    return redirect(url_for('map.main_map_page'))