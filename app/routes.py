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


@app.route('/', methods=['GET', 'POST'])
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
    return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        add_new_customer(g.conn, form.cname.data, form.gender.data,\
                         form.birthday.data, form.password.data)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/profile/<cname>')
def profile(cname):
    user = Customer(find_first_query(g.conn, cname, "cname", "customers"))
    new_password = request.args.get('password', "", type=str)
    if new_password != "":
        update_password(g.conn, new_password, user.cid)
    comments = find_all_personal_comments(g.conn, user.cid)
    return render_template('profile.html', title='Profile', user=user, comments=comments)


@app.route('/search/<keywords>', methods=['POST', 'GET'])
def search(keywords):
    form = FilterForm()
    keyword, brand, cate = keywords.split('#')
    print(keyword)
    cur_page = request.args.get('page', 1, type=int)
    filters = request.args.get('filters', '#', type=str)
    if filters == "#":
        products = search_by_keywords(g.conn, keyword, brand, cate)
    else:
        start_date, end_date, min_price, max_price, order = filters.split('#')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        products = get_sorted_result(g.conn, keyword, brand, cate, start_date, end_date, min_price, max_price, order)

    if form.validate_on_submit():
        start_date, end_date = form.start_date.data, form.end_date.data
        min_price, max_price = form.min_price.data, form.max_price.data
        order = form.order.data
        if not start_date:
            start_date = datetime.date(1000, 1, 1)
        if not end_date:
            end_date = datetime.date.today()
        if not min_price:
            min_price = 0
        if not max_price:
            max_price = 99999
        
        products = get_sorted_result(g.conn, keyword, brand, cate, start_date, end_date, min_price, max_price, order)
        print(products)
        cur_page = 1
        filters = str(start_date) + '#' + str(end_date) + '#' + str(min_price) + '#' + str(max_price) + '#' + order

    if not products:
        flash("Can not find such product in the database.")
        return redirect(url_for('index'))
    num = len(products)
    pages = num // Config.ITEM_PER_PAGE + 1
    if num % Config.ITEM_PER_PAGE == 0 and num != 0:
        pages -= 1

    if cur_page < pages:
        next_url = url_for('search', keywords=keywords, filters=filters, page=cur_page+1)
    else:
        next_url = None
    if cur_page > 1:
        prev_url = url_for('search', keywords=keywords, filters=filters, page=cur_page-1)
    else:
        prev_url = None
    products = products[(cur_page - 1) * Config.ITEM_PER_PAGE : cur_page * Config.ITEM_PER_PAGE]
    return render_template('search.html', title='Search', products=products, form=form, num=num, \
                           next_url=next_url, prev_url=prev_url)


@app.route('/product/<pid>', methods=['POST', 'GET'])
def product(pid):
    product = get_product_info(g.conn, pid)
    comments = get_all_comments(g.conn, pid)
    bform = AddToBagForm()
    cform = PostCommentForm()
    
    if request.method == 'POST' and 'delete' in request.form:
        delete_query(g.conn, 'communities', 'commid',request.form['delete'])
        flash("You have deleted your comment.")
        return redirect(url_for('product', pid=pid))

    if bform.validate_on_submit():
        try:
            cid = current_user.cid
        except AttributeError as error:
            flash("You need to log in to add in your bag!")
            return redirect(url_for('product', pid=pid))
        amount = bform.amount.data
        add_to_bag(g.conn, pid, cid, amount)
        flash("You have added the item into your bag!")
        return redirect(url_for('product', pid=pid))

    if cform.validate_on_submit():
        try:
            cid = current_user.cid
        except AttributeError as error:
            flash("You need to log in to post your comment!")
            return redirect(url_for('product', pid=pid))
        postdate = datetime.date.today()
        comment = cform.comment.data
        add_new_comment(g.conn, pid, cid, comment, postdate)
        flash("You have added your comment, thanks for sharing!")
        return redirect(url_for('product', pid=pid))

    return render_template('product.html', title='Product', product=product, \
                            comments=comments, bform=bform, cform=cform)


@app.route('/bag/<cid>', methods=['POST', 'GET'])
def bag(cid):
    items = get_the_bag(g.conn, cid)
    bsum = get_bag_sum(g.conn, cid).sum

    if request.method == 'POST' and 'delete' in request.form:
        delete_item(g.conn, 'bags', cid, request.form['delete'])
        flash("You have removed the item no.%s from your bag." % cid)
        return redirect(url_for('bag', cid=cid))
    return render_template('bag.html', title='Bag', sum='%.2f'%bsum, items=items)


@app.route('/bestsellers', methods=['POST', 'GET'])
def bestsellers():
    date = request.args.get('date', None)
    if not date:
        all_dates = get_bestsellers_date(g.conn)
        return render_template("bestsellers.html", title="Best sellers", dates=all_dates)
    else:
        products = get_specify_bestsellers(g.conn, date)
        return render_template("bestsellers.html", title="Best sellers", products=products)


@app.route('/admin/products', methods=['POST', 'GET'])
def adproducts():
    form = FilterForm()
    cur_page = request.args.get('page', 1, type=int)
    filters = request.args.get('filters', '#', type=str)

    if filters == "#":
        products = search_by_keywords(g.conn, '', '', '')
    else:
        start_date, end_date, min_price, max_price, order = filters.split('#')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        products = get_sorted_result(g.conn, '', '', '', start_date, end_date, min_price, max_price, order)

    if request.method == 'POST' and 'delete' in request.form:
        delete_query(g.conn, 'products', 'pid', request.form['delete'])
        flash("You have deleted the product from database.")
        return redirect(url_for('adproducts'))

    if form.validate_on_submit():
        start_date, end_date = form.start_date.data, form.end_date.data
        min_price, max_price = form.min_price.data, form.max_price.data
        order = form.order.data
        if not start_date:
            start_date = datetime.date(1000, 1, 1)
        if not end_date:
            end_date = datetime.date.today()
        if not min_price:
            min_price = 0
        if not max_price:
            max_price = 99999

        products = get_sorted_result(g.conn, '', '', '', start_date, end_date, min_price, max_price, order)
        cur_page = 1
        filters = str(start_date) + '#' + str(end_date) + '#' + str(min_price) + '#' + str(max_price) + '#' + order

    if not products:
        flash("Can not find such product in the database.")
        return redirect(url_for('adproducts'))
    num = len(products)
    pages = int((num + 0.1) // Config.ITEM_PER_PAGE)

    if cur_page < pages:
        next_url = url_for('adproducts', filters=filters, page=cur_page+1)
    else:
        next_url = None
    if cur_page > 1:
        prev_url = url_for('adproducts', filters=filters, page=cur_page-1)
    else:
        prev_url = None
    products = products[(cur_page - 1) * Config.ITEM_PER_PAGE : cur_page * Config.ITEM_PER_PAGE]
    return render_template('adproducts.html', title='Admin', products=products, num=num, form=form, \
                           next_url=next_url, prev_url=prev_url)


@app.route('/admin/information/product/<pid>', methods=['POST', 'GET'])
def adinfoproduct(pid):
    product = get_product_info(g.conn, pid)
    comments = get_all_comments(g.conn, pid)
    
    if request.method == 'POST':
        if 'delete' in request.form:
            delete_query(g.conn, 'communities', 'commid',request.form['delete'])
            flash("You have deleted the comment.")
            return redirect(url_for('adinfoproduct', pid=pid))

        else:
            pname = request.form.get('pname') 
            bname = request.form.get('bname')
            pdate = request.form.get('pdate')
            try:
                y, m, h = pdate.split('-')
                pdate = datetime.date(int(y), int(m), int(h))
            except:
                flash("Please enter a valid date!")
                return redirect(url_for('adinfoproduct', pid=pid))
            
            new_name = find_first_query(g.conn, pname, "pname", "products")
            if new_name and new_name.pname != product.pname:
                flash("There is alreay a product with a same name in the database!")
                return redirect(url_for('adinfoproduct', pid=pid))
            
            new_brand = find_first_query(g.conn, bname, "bname", "brands")
            if not new_brand:
                flash("There is no such company!")
                return redirect(url_for('adinfoproduct', pid=pid))
            update_product_info(g.conn, pid, pname, new_brand.bid, pdate)
            return redirect(url_for('adinfoproduct', pid=pid))

    return render_template('adinfoproduct.html', title='Product', product=product, comments=comments)


@app.route('/admin/bestsellers', methods=['POST', 'GET'])
def adbestsellers():
    date = request.args.get('date', None)
    if request.method == "POST" and 'delete' in request.form:
        pid = request.form.get('delete')
        delete_bestseller(g.conn, pid, date)
        flash("You have deleted it!")
        return redirect(url_for('adbestsellers', date=date))

    if not date:
        all_dates = get_bestsellers_date(g.conn)
        return render_template("adbestsellers.html", title="Best sellers", dates=all_dates)
    else:
        products = get_specify_bestsellers(g.conn, date)
        return render_template("adbestsellers.html", title="Best sellers", products=products)


@app.route('/admin/brands', methods=['GET', 'POST'])
def adbrands():
    order = request.args.get('order', None)
    try:
        order, sort = order.split('#')
    except:
        sort = 1

    brands = get_all_brands(g.conn, order)
    num = len(brands)
    return render_template('adbrands.html', title="Brands", \
                            brands=brands, num=num, sort=sort)


@app.route('/admin/customers', methods=['GET', 'POST'])
def adcustomers():
    order = request.args.get('order', None)
    try:
        order, sort = order.split('#')
    except:
        sort = 1

    customers = get_all_customers(g.conn, order)
    num = len(customers)
    return render_template('adcustomers.html', title="Customers", \
                            customers=customers, num=num, sort=sort)


@app.route('/admin/add', methods=['GET', 'POST'])
def add():
    item = request.args.get('item')
    if item == "brand":
        form = AddBrandForm()
    elif item == "product":
        form = AddProductForm()
    elif item == "bestseller":
        form = AddBestSellerForm()
    
    if form.validate_on_submit():
        if item == "brand":
            add_new_brand(g.conn, form.bid.data, form.bname.data, form.surplus.data)
            flash("You have added a new brand in the database!")
            return redirect(url_for('adbrands'))
        elif item == "product":
            add_new_product(g.conn, form.pid.data, form.pname.data, form.bid.data, \
                            form.cateid.data, form.price.data, form.pdate.data)
            flash("You have added a new product in the database!")
            return redirect(url_for('adproducts'))
        elif item == "bestseller":
            add_new_bestseller(g.conn, form.pid.data, form.bdate.data)
            flash("You have added a new bestseller in the database!")
            return redirect(url_for('adbestsellers'))
    
    return render_template('add.html', form=form, item=item)
