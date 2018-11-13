from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange
from app.models import get_brands_cates_list, find_first_query
from app import engine


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
        user = find_first_query(engine, cname.data, "cname", "customers")
        if user is not None:
            raise ValidationError('Please use a different username.')


class SearchForm(FlaskForm):
    keyword = StringField('Keywords')
    brand = SelectField('Choose Brand', choices=get_brands_cates_list(attr="bname", table="brands"))
    category = SelectField('Choose Category', choices=get_brands_cates_list(attr="subcatename", table="categories"))
    submit = SubmitField('Search')


class PostCommentForm(FlaskForm):
    comment = TextAreaField('Post your comment here', validators=[DataRequired(), Length(min=1, max=300)])
    submit = SubmitField('Submit')

    def validate_comment(self, comment):
        user = find_first_query(engine, comment.data, "content", "communities")
        if user is not None:
            raise ValidationError('Please say something different.')


class AddToBagForm(FlaskForm):
    amount = IntegerField('Please input amount:', validators=[NumberRange(min=1)])
    submit = SubmitField('Add to my bag')