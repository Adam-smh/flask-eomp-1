import hmac
import sqlite3
import datetime

from flask import Flask, request
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message

import cloudinary
import cloudinary.uploader
import DNS
import validate_email


# User class
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# Product class
class Product(object):
    def __init__(self, user_id, product_name, product_image_url, product_category, product_description, product_price):
        self.user_id = user_id
        self.product_name = product_name
        self.product_image_url = product_image_url
        self.product_category = product_category
        self.product_description = product_description
        self.product_price = product_price


# Database class
class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('pointOfSale.db')
        self.cursor = self.conn.cursor()

    def registration(self, first_name, last_name, email, username, password):
        # Sending user info to database
        self.cursor.execute("INSERT INTO user("
                            "first_name,"
                            "last_name,"
                            "email,"
                            "username,"
                            "password) VALUES(?, ?, ?, ?, ?)", (first_name, last_name, email, username, password))
        self.conn.commit()

    # Add product to database
    def add_product(self, user_id, product_name, product_image, product_category, product_description, product_price):

        # Upload image to cloudinary
        cloudinary.config(cloud_name='ddvdj4vy6', api_key='416417923523248',
                          api_secret='v_bGoSt-EgCYGO2wIkFKRERvqZ0')
        upload_result = None

        app.logger.info('%s file_to_upload', product_image)
        if product_image:
            upload_result = cloudinary.uploader.upload(product_image)   # Upload results
            app.logger.info(upload_result)
            # data = jsonify(upload_result)
        self.cursor.execute("INSERT INTO product (user_id, product_name, product_image_url, product_category, "
                            "product_description, product_price) VALUES (?, ?, ?, ?, ?, ?)",
                            (user_id, product_name, upload_result['url'], product_category, product_description,
                             product_price))

        self.conn.commit()

    # fetch products
    def get_products(self):
        self.cursor.execute("SELECT * FROM product")
        return self.cursor.fetchall()

    # fetch one specific product
    def view_product(self, product_id):
        self.cursor.execute('SELECT * FROM product WHERE product_id={}'.format(product_id))
        return self.cursor.fetchone()

    # edit product
    def edit_product(self, product_data, product_id):
        response = {}
        put_data = {}

        # if statements are to check if data received is not empty
        if product_data.get('product_name'):
            put_data['product_name'] = product_data.get('product_name')
            with sqlite3.connect('pointOfSale.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_name=? WHERE product_id=?", (put_data["product_name"],
                                                                                        product_id))
                conn.commit()
                response['message'] = "Update was successful"
                response['status_code'] = 200

        #
        if product_data.get('product_category'):
            put_data['product_category'] = product_data.get('product_category')
            with sqlite3.connect('pointOfSale.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_category=? WHERE product_id=?",
                               (put_data["product_category"], product_id))
                conn.commit()
                response['message'] = "Update was successful"
                response['status_code'] = 200

        if product_data.get('product_description'):
            put_data['product_description'] = product_data.get('product_description')
            with sqlite3.connect('pointOfSale.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_description=? WHERE product_id=?",
                               (put_data["product_description"], product_id))
                conn.commit()
                response['message'] = "Update was successful"
                response['status_code'] = 200

        if product_data.get('product_price'):
            put_data['product_price'] = product_data.get('product_price')
            with sqlite3.connect('pointOfSale.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET product_price=? WHERE product_id=?", (put_data["product_price"],
                                                                                         product_id))
                conn.commit()
                response['message'] = "Update was successful"
                response['status_code'] = 200

        return response

    # Delete product
    def delete_product(self, product_id):
        with sqlite3.connect('pointOfSale.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM product WHERE product_id={}'.format(product_id))
            conn.commit()


# create user table
def init_user_table():
    conn = sqlite3.connect('pointOfSale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


# Create product table
def init_product_table():
    conn = sqlite3.connect('pointOfSale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS product(product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "user_id TEXT,"
                 "product_name TEXT NOT NULL,"
                 "product_image_url TEXT NOT NULL,"
                 "product_category TEXT NOT NULL,"
                 "product_description TEXT NOT NULL,"
                 "product_price TEXT NOT NULL,"
                 "FOREIGN KEY (user_id) "
                 "REFERENCES user(user_id))")
    print('product table created successfully')
    conn.close()


init_user_table()
init_product_table()


# fetch users for JWT
def fetch_users():
    with sqlite3.connect('pointOfSale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[4], data[5]))
    return new_data


def authenticate(username, password):
    users = fetch_users()
    username_table = {u.username: u for u in users}
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    users = fetch_users()
    userid_table = {u.id: u for u in users}
    user_id = payload['identity']
    return userid_table.get(user_id, None)


# Initialise app
app = Flask(__name__)
app.debug = True

app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(hours=24)   # Extending token expiration

# Mail config
app.config['MAIL_SERVER']= "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "onfroz3@gmail.com"
app.config['MAIL_PASSWORD'] = "FwABUqBFLVzt78w#"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# mail instantiation
mail = Mail(app)

jwt = JWT(app, authenticate, identity)

CORS(app)

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity

# Registration route
@app.route('/register/', methods=['POST'])
def registration():
    response = {}

    if request.method == "POST":

        # fetch form info
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Check if form info not empty
        if not first_name or not last_name or not username or not password or not email:
            response['message'] = 'One or more entries are empty'
            response['status_code'] = 400
            return response

        elif not validate_email.validate_email(email, verify=True):
            response['message'] = 'Email not valid'
            response['status_code'] = 401
            return response

        # Check if username and/or email already exists in database
        with sqlite3.connect('pointOfSale.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE username='{}'".format(username))
            username_result = cursor.fetchone()

            cursor.execute("SELECT * FROM user WHERE email='{}'".format(email))
            email_result = cursor.fetchone()

            if username_result:
                response['message'] = 'Username already exists'
                response['status_code'] = 400
                return response

            elif email_result:
                response['message'] = 'Email already exists'
                response['status_code'] = 400
                return response

        db = Database()
        db.registration(first_name, last_name, email, username, password)

        # update
        users = fetch_users()
        username_table = {u.username: u for u in users}
        userid_table = {u.id: u for u in users}

        # Send email
        msg = Message('OnFroz3 Registration Successful', sender='onfroz3@gmail.com', recipients=[email])
        msg.body = "Salutations mother's child, \n \n" \
                   "Welcome to the frozen community! Hope you dressed appropriately. \n " \
                   "If you have any questions, " \
                   "feel free to hit us up with an email. \n \n" \
                   "Stay chilly, \n" \
                   "OnFroz3 team"
        mail.send(msg)

        response["message"] = "success"
        response["status_code"] = 201
        return response


@app.route('/add-product/<int:user_id>', methods=['POST'])
@jwt_required()
def add_product(user_id):
    response = {}

    if request.method == 'POST':
        try:
            # fetch form data
            product_name = request.form['product_name']
            product_image = request.files['product_image']
            product_category = request.form['product_category']
            product_description = request.form['product_description']
            product_price = request.form['product_price']

            # check if variables empty
            if not product_name or not product_category or not product_description or not product_price:
                response['message'] = 'One or more entries are empty'
                response['status_code'] = 400
                return response

            # check if price is a number
            int(product_price)

            # add product to database
            db = Database()
            db.add_product(user_id, product_name, product_image, product_category, product_description, product_price)

            response['message'] = "Product entered successfully"
            response['status_code'] = 200

            return response

        except ValueError:
            response['message'] = "Price must be integer"
            response['status_code'] = 400

            return response


@app.route('/show-products/')
def fetch_products():
    response = {}

    db = Database()

    response['products'] = db.get_products()  # fetch products
    response['message'] = 'Products retrieved successfully'
    response['status_code'] = 200

    return response


@app.route('/view-product/<int:product_id>/')
def view_product(product_id):
    response = {}

    db = Database()
    product = db.view_product(product_id)   # fetch specific product with product id

    response['message'] = 'Successfully retrieved product info'
    response['status_code'] = 200
    response['product'] = product

    return response


@app.route('/edit-product/<int:product_id>/', methods=['PUT'])
@jwt_required()
def edit_product(product_id):
    response = None

    if request.method == 'PUT':
        incoming_data = dict(request.json)
        db = Database()
        response = db.edit_product(incoming_data, product_id)

    return response


@app.route('/delete-product/<int:product_id>/')
@jwt_required()
def delete_product(product_id):
    response = {}

    db = Database()
    db.delete_product(product_id)

    response['message'] = 'Product deleted successfully'
    response['status_code'] = 200

    return response


if __name__ == '__main__':
    app.run()
users = {"username": 'wow'}

def update():
    global users
    users.username = 'whoa'

print(users)