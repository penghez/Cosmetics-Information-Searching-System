from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange, Optional
from app.models import get_brands_cates_list, find_first_query, find_bestsellers
from app import engine
import datetime


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


class FilterForm(FlaskForm):
    start_date = DateField('Start data', format='%Y/%m/%d', validators=[Optional()])
    end_date = DateField('End data', format='%Y/%m/%d', validators=[Optional()])
    min_price = IntegerField('Min price', validators=[Optional()])
    max_price = IntegerField('Max price', validators=[Optional()])
    order = SelectField('Price order', choices=[('price DESC', 'Price High to Low'), ('price ASC', 'Price Low to High'), \
                                                ('pdate DESC', 'Date High to Low'), ('pdate ASC', 'Date Low to High')])
    submit = SubmitField('Apply')

    def validate_max_price(self, max_price):
        if self.min_price.data and self.min_price.data > max_price.data:
            raise ValidationError('Max price should not smaller than min price.')

    def validate_end_date(self, end_date):
        if self.start_date.data and self.start_date.data > end_date.data:
            raise ValidationError('End date should not smaller than start date.')


class AddBrandForm(FlaskForm):
    bid = IntegerField('Brand ID', validators=[DataRequired()])
    bname = StringField('Brand Name', validators=[DataRequired()])
    surplus = StringField('Surplus', default="0")
    submit = SubmitField('Apply')

    def validate_bid(self, bid):
        brand = find_first_query(engine, bid.data, "bid", "brands")
        if brand is not None:
            raise ValidationError('Please use a different ID.')
    
    def validate_bname(self, bname):
        brand = find_first_query(engine, bname.data, "bname", "brands")
        if brand is not None:
            raise ValidationError('Please use a different name.')


class AddProductForm(FlaskForm):
    pid = IntegerField('Product ID', validators=[DataRequired()])
    pname = StringField('Product Name', validators=[DataRequired()])
    bid = IntegerField('Brand ID', validators=[DataRequired()])
    cateid = IntegerField('Category ID', validators=[DataRequired()])
    pdate = DateField('Produce Date', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    submit = SubmitField('Apply')

    def validate_pid(self, pid):
        product = find_first_query(engine, pid.data, "pid", "products")
        if product is not None:
            raise ValidationError('Please use a different ID.')
    
    def validate_pname(self, pname):
        product = find_first_query(engine, pname.data, "pname", "products")
        if product is not None:
            raise ValidationError('Please use a different name.')

    def validate_bid(self, bid):
        brand = find_first_query(engine, bid.data, "bid", "brands")
        if brand is None:
            raise ValidationError('No such company found!')

    def validate_cateid(self, cateid):
        cate = find_first_query(engine, cateid.data, "cateid", "categories")
        if cate is not None:
            raise ValidationError('No such category found!')


class AddBestSellerForm(FlaskForm):
    pid = IntegerField('Product ID', validators=[DataRequired()])
    bdate = DateField('Bestseller Date', format='%Y/%m/%d', validators=[DataRequired()])
    submit = SubmitField('Apply')

    def validate_pid(self, pid):
        bs = find_bestsellers(engine, pid.data, self.bdate.data)
        if bs is not None:
            raise ValidationError('It is already in the database!')
    