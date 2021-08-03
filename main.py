import hmac
import sqlite3
import datetime

from flask import *
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def init_user_table():
    conn = sqlite3.connect('pointOfSale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


def init_product_table():
    conn = sqlite3.connect('pointOfSale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS product(product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "user_id TEXT,"
                 "product_name TEXT NOT NULL,"
                 "product_category TEXT NOT NULL,"
                 "product_description TEXT NOT NULL,"
                 "product_price TEXT NOT NULL,"
                 "FOREIGN KEY (user_id) "
                 "REFERENCES user(user_id))")
    print('product table created successfully')
    conn.close()


init_user_table()
init_product_table()


def fetch_users():
    with sqlite3.connect('pointOfSale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


users = fetch_users()
username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(hours=24)
CORS(app)

jwt = JWT(app, authenticate, identity)


@app.route('/register/', methods=['POST'])
def registration():
    response = {}

    if request.method == "POST":

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("pointOfSale.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password) VALUES(?, ?, ?, ?)", (first_name, last_name, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/add-product/', methods=['POST'])
@jwt_required()
def add_product():
    response = {}

    if request.method == 'POST':
        user_id = request.form['user_id']
        product_name = request.form['product_name']
        product_category = request.form['product_category']
        product_description = request.form['product_description']
        product_price = request.form['product_price']

        with sqlite3.connect('pointOfSale.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO product (user_id, product_name, product_category, product_description, "
                           "product_price) VALUES (?, ?, ?, ?, ?)", (user_id, product_name, product_category,
                                                                     product_description, product_price))
            conn.commit()

        response['message'] = "Product entered successfully"
        response['status_code'] = 200

        return response


@app.route('/show-products/')
def get_products():
    response = {}

    with sqlite3.connect('pointOfSale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")
        products = cursor.fetchall()
        print(products)

    response['products'] = products
    response['message'] = 'Products retrieved successfully'
    response['status_code'] = 200

    return response


@app.route('/view-product/<int:product_id>/')
def view_product(product_id):
    response = {}

    with sqlite3.connect('pointOfSale.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM product WHERE product_id={}'.format(product_id))
        product = cursor.fetchone()

    response['message'] = 'Successfully retrieved product info'
    response['status_code'] = 200
    response['product'] = product

    return response


@app.route('/edit-product/<int:product_id>/', methods=['PUT'])
@jwt_required()
def edit_product(product_id):
    response = {}

    if request.method == 'PUT':
        incoming_data = dict(request.json)
        put_data = {}

        if incoming_data.get('product_name'):
            put_data['product_name'] = incoming_data.get('product_name')
            with sqlite3.connect('pointOfSale.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_name=? WHERE product_id=?", (put_data["product_name"],
                                                                                        product_id))
                conn.commit()
                response['message'] = "Update was successful"
                response['status_code'] = 200

        if incoming_data.get('product_category'):
            put_data['product_category'] = incoming_data.get('product_category')
            with sqlite3.connect('pointOfSale.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_category=? WHERE product_id=?",
                               (put_data["product_category"], product_id))
                conn.commit()
                response['message'] = "Update was successful"
                response['status_code'] = 200

        if incoming_data.get('product_description'):
            put_data['product_description'] = incoming_data.get('product_description')
            with sqlite3.connect('pointOfSale.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_description=? WHERE product_id=?",
                               (put_data["product_description"], product_id))
                conn.commit()
                response['message'] = "Update was successful"
                response['status_code'] = 200

        if incoming_data.get('product_price'):
            put_data['product_price'] = incoming_data.get('product_price')
            with sqlite3.connect('pointOfSale.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_price=? WHERE product_id=?", (put_data["product_price"],
                                                                                         product_id))
                conn.commit()
                response['message'] = "Update was successful"
                response['status_code'] = 200

    return response


@app.route('/delete-product/<int:product_id>/')
@jwt_required()
def delete_product(product_id):
    response = {}

    with sqlite3.connect('pointOfSale.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM product WHERE product_id={}'.format(product_id))
        conn.commit()

        response['message'] = 'Product deleted successfully'
        response['status_code'] = 200

    return response


if __name__ == '__main__':
    app.run(debug=True)
