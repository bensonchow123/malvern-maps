from flask import Blueprint, render_template
from forms import LoginForm
report_system = Blueprint("report_system", __name__)

@report_system.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        pass
    return render_template('login.html', form=form)

@report_system.route('/register')
def register():
    return render_template('register.html')

@report_system.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')
