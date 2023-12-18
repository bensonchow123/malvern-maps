from os import getenv
from re import search
from bson.objectid import ObjectId
from datetime import datetime, timedelta

from wtforms import StringField, SubmitField, SelectField, PasswordField, TextAreaField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, StopValidation, Length, NumberRange, Optional
from wtforms.widgets import ListWidget, CheckboxInput
from flask_wtf import FlaskForm
from shortest_path_calculations import get_nodes
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

    if node_data.casefold() not in name_of_nodes:
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
    inputted_email = field.data
    staff_emails_db = malvern_maps_db["staff-emails"]
    staff_emails = staff_emails_db.find_one({"email": inputted_email})
    if not staff_emails:
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

class ReportEventForm(FlaskForm):
    node_to_report = StringField('Node to report', validators=[DataRequired(), is_valid_node])
    description = TextAreaField('Reason', validators=[DataRequired(), Length(min=10, max=1000)])
    submit_report = SubmitField('Submit report')

def is_valid_reported_event(form, field):
    event_id = field.data
    reported_events = malvern_maps_db["reported-events"]
    try:
        event_id = ObjectId(event_id)
    except Exception:
        field.errors.append("Invalid event ID")
        raise StopValidation()

    found_event = reported_events.find_one({"_id": event_id})
    if not found_event:
        field.errors.append("Event with this ID not found")
        raise StopValidation()

class RemoveReportedEventForm(FlaskForm):
    event_to_remove_id = StringField('Event ID', validators=[DataRequired(), is_valid_reported_event])
    submit_event_to_remove = SubmitField('Remove event')

def prevent_duplicate_staff_info(form, field):
    email = field.data
    action = form.action.data
    staff_emails = malvern_maps_db["staff-emails"]
    found_email = staff_emails.find_one({"email": email})
    if found_email:
        if action == 'admin' and found_email["admin"]:
            field.errors.append("Email already an admin")
            raise StopValidation()

        elif action == 'staff' and not found_email["admin"]:
            field.errors.append("Email already a staff")
            raise StopValidation()

    elif action == 'remove' and not found_email:
        field.errors.append("Email is not a staff member")
        raise StopValidation()

class ManageStaffForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            StopValidationEmail(),
            prevent_duplicate_staff_info
        ]
    )
    action = SelectField(
        'Type',
        choices=[('staff', 'Set as staff'), ('admin', 'Set as admin'), ('remove', 'Remove from staff')],
        validators=[DataRequired()]
    )
    submit_staff_action = SubmitField('Submit staff action')

class AtLeastOneField(object):
    def __init__(self, other_field_name):
        self.other_field_name = other_field_name
        self.error_message = f'At least one field must have data'

    def __call__(self, form, field):
        try:
            other_field = form[self.other_field_name]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.other_field_name)
        if not field.data and not other_field.data:
            field.errors.append(self.error_message)
            other_field.errors = []
            other_field.errors.append(self.error_message)
            raise StopValidation()
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class FilterEventsForm(FlaskForm):
    groups_to_filter = MultiCheckboxField(
        'Filter by groups',
        choices=[
            ('c', 'car paths'),
            ('h', 'shortcuts'),
            ('s', 'stairs'),
            ('w', 'walkways')
        ],
        validators=[
            AtLeastOneField('number_to_filter')
        ]
    )
    number_to_filter = IntegerField(
        'filter by group number',
        validators=[
            AtLeastOneField('groups_to_filter'),
            Optional(),
            NumberRange(min=1, max=78),
        ]
    )
    submit_filter_param = SubmitField('Filter nodes')