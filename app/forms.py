from flask_wtf import FlaskForm
from wtforms  import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired



class LoginForm(FlaskForm):
	mturk_id = StringField('MTurk ID', validators = [DataRequired()])
	submit = SubmitField('Begin Experiment')
