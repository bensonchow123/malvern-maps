from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm


class ShortestPathCalculationForm(FlaskForm):
    starting_point = StringField('Starting point', validators=[DataRequired(), Email()])
    destination = StringField('Destination', validators=[DataRequired()])
    remove_stairs = SelectField('Remove stairs', choices=[('no', 'No'),('yes', 'Yes')])
    allow_shortcuts = SelectField('Allow shortcuts', choices=[('no', 'No'),('yes', 'Yes')])
    only_walkways = SelectField('Only walkways', choices=[('no', 'No'), ('yes', 'Yes')])
    only_car_paths = SelectField('Only car paths', choices=[('no', 'No'), ('yes', 'Yes')])
    submit = SubmitField('Begin calculation')
