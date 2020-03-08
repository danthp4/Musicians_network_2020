from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, SelectField, IntegerField, TextAreaField, BooleanField, \
    SelectMultipleField, widgets
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from app.models import Profile


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ProfileForm(FlaskForm):
    description = TextAreaField('Profile description', validators=[DataRequired()])
    profile_name = StringField('Profile Name', validators=[DataRequired()])
    location = SelectField(u'City', choices=[('ldn', 'London'), ('mnc', 'Manchester'), ('bln', 'Berlin')])
    genre = MultiCheckboxField(u'Genre', choices=[('rck', 'Rock'), ('dnb', 'Drum and Bass'), ('tcn', 'Techno')])

    submit = SubmitField('Save & Submit')
