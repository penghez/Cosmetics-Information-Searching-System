from flask import render_template, flash, redirect, url_for, request, g
from app import app, engine
from app.forms import *
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
from config import Config
import datetime


@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        keyword, brand, cate = form.keyword.data, form.brand.data, form.category.data
        keyword_list = keyword + "#" + brand + "#" + cate.split('/')[0]
        return redirect(url_for('search', keywords=keyword_list))

    return render_template('index.html', title='Home', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        customer = find_first_query(g.conn, form.cname.data, "cname", "customers")
        if customer is None or customer.password != form.password.data:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        customer = Customer(customer)
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
        add_new_customer(g.conn, form.cname.data, form.gender.data, form.birthday.data, form.password.data)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/profile/<cname>')
def profile(cname):
    user = Customer(find_first_query(g.conn, cname, "cname", "customers"))
    return render_template('profile.html', title='Profile', user=user)


@app.route('/search/<keywords>', methods=['POST', 'GET'])
def search(keywords):
    form = FilterForm()
    keyword, brand, cate = keywords.split('#')
    products = search_by_keywords(g.conn, keyword, brand, cate)
    if not products:
        flash("Can not find such product in the database.")
        return redirect(url_for('index'))

    if form.validate_on_submit():
        start_date, end_date = form.start_date.data, form.end_date.data
        min_price, max_price = form.min_price.data, form.max_price.data
        order = form.order.data
        if not start_date:
            start_date = datetime.datetime.strptime('1000/01/01', '%Y/%m/%d') 
        if not end_date:
            end_date = datetime.date.today()
        if not min_price:
            min_price = 0
        if not max_price:
            max_price = 99999
        products = get_sorted_result(g.conn, keyword, brand, cate, start_date, end_date, min_price, max_price, order)
        return render_template('search.html', title='Search', products=products, form=form)
    return render_template('search.html', title='Search', products=products, form=form)


@app.route('/product/<pid>', methods=['POST', 'GET'])
def product(pid):
    product = get_product_info(g.conn, pid)
    comments = get_all_comments(g.conn, pid)
    bform = AddToBagForm()
    cform = PostCommentForm()
    if bform.validate_on_submit():
        if not current_user:
            flash("You need to log in to add in your bag!")
            return redirect(url_for('product', pid=pid))
        cid = current_user.cid
        amount = bform.amount.data
        add_to_bag(g.conn, pid, cid, amount)
        flash("You have added the item into your bag!")
        return redirect(url_for('product', pid=pid))

    if cform.validate_on_submit():
        if not current_user:
            flash("You need to log in to post your comment!")
            return redirect(url_for('product', pid=pid))
        postdate = datetime.date.today()
        cid = current_user.cid
        comment = cform.comment.data
        add_new_comment(g.conn, pid, cid, comment, postdate)
        flash("You have added your comment, thanks for sharing!")
        return redirect(url_for('product', pid=pid))
    return render_template('product.html', title='Product', product=product, comments=comments, bform=bform, cform=cform)


@app.route('/bag/<cid>', methods=['POST', 'GET'])
def bag(cid):
    items = get_the_bag(g.conn, cid)
    bsum = 0
    for i in items:
        bsum += i.price * i.amount
    if request.method == 'POST':
        delete_from_bag(g.conn, cid, request.form['deleted'])
        flash("You have removed the item no.%s from your bag." % cid)
        return redirect(url_for('bag', cid=cid))
    return render_template('bag.html', title='Bag', sum='%.2f'%bsum, items=items)