from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Customers, Products


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        if keyword:
            return redirect(url_for('search', keywords=keyword))
        else:
            flash('Please type in your keywords!')
            return redirect(url_for('index'))
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        customer = Customers.query.filter_by(cname=form.cname.data).first()
        if customer is None or customer.password != form.password.data:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(customer, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = Customers(cname=form.cname.data, birthday=form.birthday.data, 
                             gender=form.gender.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/profile/<cname>')
@login_required
def profile(cname):
    user = Customers.query.filter_by(cname=cname).first_or_404()
    return render_template('profile.html', user=user)


@app.route('/search/<keywords>')
def search(keywords):
    products = Products.query.filter(Products.pname.like('%'+keywords+'%')).all()
    if not products:
        flash("Can not find such product in the database.")
        return redirect(url_for('index'))
    return render_template('search.html', products=products)


@app.route('/product/<pid>')
def product(pid):
    product = Products.query.filter_by(pid=pid).first_or_404()
    return render_template('product.html', product=product)