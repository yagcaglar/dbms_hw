from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, RadioField,DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from server import cur


class RegistrationForm(FlaskForm):
	name= StringField('Name', validators=[DataRequired()])
	surname = StringField('Surname', validators=[DataRequired()])
	username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email',validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
	is_acm =RadioField('Accompanist',coerce = int, choices = [(1, 'Accompanist'), (0, 'User')], default = 0)
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		cur.execute("SELECT username FROM person where username='%s'" % username.data)
		user = cur.fetchone()
		if user is not None:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		cur.execute("SELECT mail FROM person where mail='%s'" % email)
		user = cur.fetchone()
		if user is not None:
			raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
	username = StringField('username',validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')
	
class CommentForm(FlaskForm):
	content = StringField('Content', validators=[DataRequired()])
	submit = SubmitField('Send comment')

class AddInfoForm(FlaskForm):
	phone = StringField('phone')
	city = StringField('city')
	university = StringField('university')
	price = IntegerField('price')

class ReservationForm(FlaskForm):
	date = DateField('date',validators=[DataRequired()])
	city = StringField('city',validators=[DataRequired()])

class ExperienceForm(FlaskForm):
	year = IntegerField('date',validators=[DataRequired()])
	city = StringField('city',validators=[DataRequired()])

class UpdateForm(FlaskForm):
	name= StringField('Name', validators=[DataRequired()])
	surname = StringField('Surname', validators=[DataRequired()])
	username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
	mail = StringField('Email',validators=[DataRequired(), Email()])

class UpdateAcm(FlaskForm):
	name= StringField('Name', validators=[DataRequired()])
	surname = StringField('Surname', validators=[DataRequired()])
	username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
	mail = StringField('Email',validators=[DataRequired(), Email()])
	phone = StringField('phone')
	city = StringField('city')
	university = StringField('university')
	price = IntegerField('price')

class ComposerForm(FlaskForm):
	name= StringField('Name', validators=[DataRequired()])
	surname = StringField('Surname', validators=[DataRequired()])