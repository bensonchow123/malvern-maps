from flask import Blueprint, render_template
from forms import LoginForm, RegisterForm, PasswordResetForm
report_system = Blueprint("report_system", __name__)

@report_system.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        pass
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
