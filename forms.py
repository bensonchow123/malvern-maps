from json import load

from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf import FlaskForm


class IsValidNode():
    def __call__(self, form, field):
        field_data = field.data
        print(field_data)

        with open('./static/json/nodes.json', 'r') as nodes_database:
            nodes = load(nodes_database)

            name_of_nodes = list(nodes.keys())

            if field_data not in name_of_nodes:
                raise ValidationError("Invalid node!")
class OnlyOneYes():
    def __init__(self, fieldname1, fieldname2):
        self.fieldname1 = fieldname1
        self.fieldname2 = fieldname2

    def __call__(self, form, field):
        if form[self.fieldname1].data == 'yes' and form[self.fieldname2].data == 'yes':
            raise ValidationError("Can't pick both!")


class ShortestPathCalculationForm(FlaskForm):
    starting_point = StringField('Starting point', validators=[DataRequired(), IsValidNode()])
    destination = StringField('Destination', validators=[DataRequired(), IsValidNode()])
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



