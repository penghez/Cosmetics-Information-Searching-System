from app import db, login
from flask_login import UserMixin

class Customers(UserMixin, db.Model):
    __tablename__ = 'customers'

    cid = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(64))
    gender = db.Column(db.String(32))
    password = db.Column(db.String(128))
    birthday = db.Column(db.Date)

    def get_id(self):
        return self.cid


class Brands(db.Model):
    __tablename__ = 'brands'

    bid = db.Column(db.Integer, primary_key=True)
    bname = db.Column(db.String(128))
    surplus = db.Column(db.String(64))
    categories = db.relationship('Categories', backref='brands', lazy='dynamic')
    products = db.relationship('Products', backref='brands', lazy='dynamic')


class Categories(db.Model):
    __tablename__ = 'categories'

    cateid = db.Column(db.Integer, primary_key=True)
    bid = db.Column(db.Integer, db.ForeignKey('brands.bid'))
    pricateid = db.Column(db.Integer)
    pricatename = db.Column(db.String(64))
    subcateid = db.Column(db.Integer)
    subcatename = db.Column(db.String(64))
    products = db.relationship('Products', backref='categories', lazy='dynamic')


class Products(db.Model):
    __tablename__ = 'products'

    pid = db.Column(db.Integer, primary_key=True)
    bid = db.Column(db.Integer, db.ForeignKey('brands.bid'), nullable=False)
    pname = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float, nullable=False)
    pdate = db.Column(db.Date)
    cateid = db.Column(db.Integer, db.ForeignKey('categories.cateid'))
    brands = db.backref('brands')


@login.user_loader
def load_user(cid):
    return Customers.query.get(int(cid))