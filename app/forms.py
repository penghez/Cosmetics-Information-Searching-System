from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Customers


class LoginForm(FlaskForm):
    cname = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    cname = StringField('Name', validators=[DataRequired()])
    birthday = DateField('Birthday (YYYY/MM/DD)', format='%Y/%m/%d')
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female'), ('N', 'Not to tell')])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_cname(self, cname):
        user = Customers.query.filter_by(cname=cname.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
