"""
Class for Program form data to be collected
"""

from constants import *

from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms.fields import SubmitField, SelectField
from wtforms.validators import DataRequired, Email, InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed


class ProgramForm(FlaskForm):
    program = FileField('Program Source File:', validators=[
        FileRequired('There\'s no file!'),
        FileAllowed(PROGRAMS, 'Only the following file types are allowed: {}'.format(
            ', '.join(PROGRAMS)))
    ])
    email = EmailField(
        'Email:', validators=[DataRequired('You need to add an email!'), Email('This is not an email!')])
    problem = SelectField('Problem:', choices=[(str(x), 'Problem {}'.format(x)) for x in PROBLEMS],
                          validators=[DataRequired('Select a problem!')])
    submit = SubmitField("Run It!")
