from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField
from wtforms.validators import DataRequired


class EnterData(FlaskForm):
    file = FileField('Please submit fingerprint data formatted in csv here:',
                     validators=[DataRequired(message='Please enter fingerprint data correctly.'), FileAllowed(['csv'])])
    submit = SubmitField('Submit data')
