from json import load
from os import getenv
from re import search
from datetime import datetime, timedelta

from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, StopValidation
from flask_wtf import FlaskForm
from shortest_path_calculation import get_nodes
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_bcrypt import check_password_hash

load_dotenv()

malvern_maps_cluster = MongoClient(getenv("MONGODB_URL"))
malvern_maps_db = malvern_maps_cluster["malvern-maps"]

def is_valid_node(form, field):
    node_data = field.data
    nodes = get_nodes()
    name_of_nodes = list(nodes.keys())

    if node_data not in name_of_nodes:
        raise ValidationError("Invalid node!")

class OnlyOneYes:
    def __init__(self, fieldname1, fieldname2):
        self.fieldname1 = fieldname1
        self.fieldname2 = fieldname2

    def __call__(self, form, field):
        if form[self.fieldname1].data == 'yes' and form[self.fieldname2].data == 'yes':
            raise ValidationError("Can't pick both!")

class ShortestPathCalculationForm(FlaskForm):
    starting_point = StringField('Starting point', validators=[DataRequired(), is_valid_node])
    destination = StringField('Destination', validators=[DataRequired(), is_valid_node])
    remove_stairs = SelectField('Remove stairs', choices=[('no', 'No'),('yes', 'Yes')])
    allow_shortcuts = SelectField('Allow shortcuts', choices=[('no', 'No'),('yes', 'Yes')])
    only_walkways = SelectField(
        'Only walkways',
        choices=[('no', 'No'), ('yes', 'Yes')],
        validators=[OnlyOneYes('only_walkways', 'only_car_paths')]
    )
    only_car_paths = SelectField(
        'Only car paths', choices=[('no', 'No'), ('yes', 'Yes')],
        validators=[OnlyOneYes('only_walkways', 'only_car_paths')]
    )
    submit = SubmitField('Begin calculation')


class LoginValidator:
    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, form, field):
        if not hasattr(form, 'found_account'):
            form.found_account = malvern_maps_db["registered-accounts"].find_one({"email": form.email.data})
        found_account = form.found_account

        if not found_account:
            if self.field_name == 'email':
                form.email.errors.append('Email not registered, register an account')
                raise ValidationError()

        elif not found_account["verified"]:
            if self.field_name == 'email':
                form.email.errors.append(
                    "Please verify your account via email or re-register if needed"
                )
                raise ValidationError()

        else:
            if self.field_name == 'password':
                if not check_password_hash(found_account["password"], form.password.data):
                    form.password.errors.append('Incorrect password')
                    raise ValidationError()

class StopValidationEmail(Email):
    def __call__(self, form, field):
        try:
            super().__call__(form, field)
        except StopValidation:
            raise
        except ValueError as error:
            field.errors.append(str(error))
            raise StopValidation()

def is_email_allowed(form, field):
    with open("./static/json/staff_email.json") as staffs:
        allowed_emails = load(staffs)
    if field.data not in allowed_emails.keys():
        field.errors.append("Email not allowed to register an account")
        raise StopValidation()

def is_email_registered(form, field):
    found_account = malvern_maps_db["registered-accounts"].find_one({"email": form.email.data})
    if found_account:
        if not found_account["verified"]:
            malvern_maps_db["registered-accounts"].delete_many({"email": form.email.data})
        else:
            field.errors.append("Email already registered, reset password if forgotten")
            raise StopValidation()

def is_password_valid(form, field):
    password = field.data
    length_error = len(password) < 8
    symbol_error = search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None

    if length_error and symbol_error:
        field.errors.append('Password must be 8+ characters and contain 1+ symbol')
        raise ValidationError()
    elif length_error:
        field.errors.append('Password must be 8+ characters')
        raise ValidationError()
    elif symbol_error:
        field.errors.append('Password must contain 1+ symbol')
        raise ValidationError()

def is_email_registered_and_verified(form, field):
    found_account = malvern_maps_db["registered-accounts"].find_one({"email": form.email.data})
    if found_account:
        if not found_account["verified"]:
            field.error.append("Email not verified, check inbox or re-verify.")
            raise StopValidation()
    else:
        field.error.append('No account found with that email.')
        raise StopValidation()

def is_exceeded_reset_limit(form, field):
    password_resets = malvern_maps_db["password-resets"]
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    email = form.email.data
    resets_in_last_day = password_resets.count_documents(
        {"email": email, "timestamp": {"$gt": yesterday, "$lt": now}}
    )
    if resets_in_last_day >= 3:
        field.errors.append("Password reset limit reached. Please try again tomorrow")
        raise StopValidation()

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(),
        StopValidationEmail(),
        LoginValidator('email')
    ])
    password = PasswordField('Password', validators=[DataRequired(), LoginValidator('password')])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            StopValidationEmail(),
            is_email_allowed,
            is_email_registered
        ]
    )
    password = PasswordField('Password',validators=[DataRequired(), is_password_valid])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('register')

class PasswordResetForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            StopValidationEmail(),
            is_email_registered_and_verified,
            is_exceeded_reset_limit
        ]
    )
    new_password = PasswordField('New Password', validators=[DataRequired(), is_password_valid])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('reset password')