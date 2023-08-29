from json import load
from os import getenv

from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from flask_wtf import FlaskForm
from shortest_path_calculation import get_nodes
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_bcrypt import check_password_hash

malvern_maps_cluster = MongoClient(getenv("MongoDbSecretKey"))
malvern_maps_db = malvern_maps_cluster["malvern_maps"]

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
    def __init__(self, field_name, message=None):
        self.field_name = field_name
        self.message = message

    def __call__(self, form, field):
        if not hasattr(form, 'found_account'):
            form.found_account = malvern_maps_db["registered_accounts"].find_one({"email": form.email.data})
        found_account = form.found_account

        if not found_account:
            form[self.field_name].errors.append('Email not registered, register an account')
            raise ValidationError()

        elif not found_account["verified"]:
            form[self.field_name].errors.append(
                'Email not verified, check your email to verify your account<br>'
                'Reregister if you did not receive an email'
            )
            raise ValidationError()

        elif not check_password_hash(found_account["password"], form.password.data):
            form[self.field_name].errors.append('Incorrect password')
            raise ValidationError()

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email(), LoginValidator('email')])
    password = PasswordField('Password', validators=[DataRequired(), LoginValidator('password')])
    submit = SubmitField('Sign In')

