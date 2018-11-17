from app import login, app, engine
from config import Config


class Customer(object):
    def __init__(self, fetch):
        self.cname = fetch.cname
        self.cid = fetch.cid
        self.password = fetch.password
        self.gender = fetch.gender
        self.birthday = fetch.birthday
    
    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.cid


@login.user_loader
def load_user(cid):
    return find_first_query(engine, cid, "cid", "customers")


def find_first_query(conn, data, attr, table):
    sql_text = '''
        SELECT * 
        FROM %s 
        WHERE %s = '%s'
    ''' % (table, attr, data)
    cursor = conn.execute(sql_text)
    fetch = cursor.first()
    cursor.close()
    return fetch


def search_by_keywords(conn, keyword, brand, cate):
    sql_text = '''
        SELECT * 
        FROM products P, brands B, categories C
        WHERE P.bid = B.bid and C.cateid = P.cateid and lower(P.pname) LIKE '%%%%%s%%%%' and
              lower(B.bname) LIKE '%%%%%s%%%%' and lower(C.subcatename) LIKE '%%%%%s%%%%'
    ''' % (keyword.lower(), brand.lower(), cate.lower())
    cursor = conn.execute(sql_text)
    fetch = cursor.fetchall()
    cursor.close()
    return fetch


def get_product_info(conn, pid):
    sql_text = '''
        SELECT * 
        FROM products P, brands B, categories C
        WHERE P.bid = B.bid and P.cateid = C.cateid and P.pid = %s
    ''' % pid
    cursor = conn.execute(sql_text)
    fetch = cursor.first()
    cursor.close()
    return fetch


def add_new_customer(conn, cname, gender, birthday, password):
    sql_text = '''
        INSERT INTO customers 
        (cname, gender, birthday, password) 
        VALUES 
        ('%s', '%s', '%s', '%s')
    ''' % (cname, gender, birthday, password)
    cursor = conn.execute(sql_text)
    cursor.close()


def add_new_comment(conn, pid, cid, comment, postdate):
    sql_text = '''
        INSERT INTO communities 
        (pid, cid, content, postdate) 
        VALUES 
        ('%s', '%s', '%s', '%s')
    ''' % (pid, cid, comment, postdate)
    cursor = conn.execute(sql_text)
    cursor.close()


def get_all_comments(conn, pid):
    sql_text = '''
        SELECT *
        FROM communities C1, customers C2
        WHERE C1.pid = %s and C1.cid = C2.cid
    ''' % pid
    cursor = conn.execute(sql_text)
    fetch = cursor.fetchall()
    cursor.close()
    return fetch


def add_to_bag(conn, pid, cid, amount):
    sql_text = '''
        SELECT *
        FROM bags
        WHERE pid=%s and cid=%s
    ''' % (pid, cid)
    cursor = conn.execute(sql_text)
    fetch = cursor.first()
    if not fetch:
        sql_text = '''
            INSERT INTO bags 
            (pid, cid, amount) 
            VALUES 
            (%s, %s, %s)
        ''' % (pid, cid, amount)
    else:
        sql_text = '''
            UPDATE bags 
            SET amount = %s 
            WHERE pid = %s and cid = %s
        ''' % (fetch.amount+amount, pid, cid)
    cursor = conn.execute(sql_text)
    cursor.close()


def delete_item(conn, table, cid, pid):
    sql_text = '''
        DELETE 
        FROM %s
        WHERE cid = %s and pid = %s 
    ''' % (table, cid, pid)
    cursor = conn.execute(sql_text)
    cursor.close()


def delete_comment(conn, commid):
    sql_text = '''
        DELETE 
        FROM communities
        WHERE commid = %s 
    ''' % commid
    cursor = conn.execute(sql_text)
    cursor.close()


def find_all_personal_comments(conn, cid):
    sql_text = '''
        SELECT *
        FROM communities
        WHERE cid = %s
    ''' % cid
    cursor = conn.execute(sql_text)
    fetch = cursor.fetchall()
    cursor.close()
    return fetch


def get_the_bag(conn, cid):
    sql_text = '''
        SELECT *
        FROM bags B, products P
        WHERE B.cid = %s and P.pid = B.pid
    ''' % cid
    cursor = conn.execute(sql_text)
    fetch = cursor.fetchall()
    cursor.close()
    return fetch


def get_sorted_result(conn, keyword, brand, cate, start_date, end_date, min_price, max_price, order):
    sql_text = '''
        WITH R AS (SELECT * 
                        FROM products P, brands B, categories C
                        WHERE P.bid = B.bid and C.cateid = P.cateid and P.pname LIKE '%%%%%s%%%%' and
                            B.bname LIKE '%%%%%s%%%%' and C.subcatename LIKE '%%%%%s%%%%')
        SELECT *
        FROM R
        WHERE R.price >= %s and R.price <= %s and R.pdate >= '%s' and R.pdate <= '%s'
        ORDER BY R.%s
    ''' % (keyword, brand, cate, min_price, max_price, start_date, end_date, order)
    cursor = conn.execute(sql_text)
    fetch = cursor.fetchall()
    cursor.close()
    return fetch


def update_password(conn, password, cid):
    sql_text = '''
        UPDATE customers 
        SET password=%s 
        WHERE cid=%s
    ''' % (password, cid)
    cursor = conn.execute(sql_text)
    cursor.close()


def get_brands_cates_list(attr, table, conn=engine):
    sql_text = "SELECT %s FROM %s" % (attr, table)
    cursor = conn.execute(sql_text)
    fetch = cursor.fetchall()
    cursor.close()
    name_list = []
    name_list.append(('', 'N/A'))
    for f in fetch:
        if attr == 'bname' and not (f.bname, f.bname) in name_list:
            name_list.append((f.bname, f.bname))
        if attr == 'subcatename' and not (f.subcatename, f.subcatename) in name_list:
            name_list.append((f.subcatename, f.subcatename))
    return name_list