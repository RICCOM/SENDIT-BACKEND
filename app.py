from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Parcel, Admin, DeliveryHistory, Notification, ParcelType, Driver
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes by default
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL="/swagger"
API_URL="/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Access API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Configurations for SQLite

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Utility Functions
def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

# Routes
@app.route('/')
def home():
    return "<h1>SendIT Courier Service</h1>"

@app.route('/users', methods=['GET', 'POST'])
@cross_origin()
def users():
    if request.method == 'GET':
        users = User.query.all()
        return jsonify([user.serialize() for user in users])
    
    elif request.method == 'POST':
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=hashed_password,
            phone=data.get('phone')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.serialize()), 201

@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@cross_origin()
def user_detail(id):
    user = User.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(user.serialize())
    
    elif request.method == 'PATCH':
        data = request.get_json()
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'password' in data:
            user.password = generate_password_hash(data['password'])
        db.session.commit()
        return jsonify(user.serialize())
    
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 204

@app.route('/users/login', methods=['POST'])
@cross_origin()
def user_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = authenticate_user(username, password)
    if user:
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/parcels', methods=['GET', 'POST'])
@cross_origin()
def parcels():
    if request.method == 'GET':
        parcels = Parcel.query.all()
        return jsonify([parcel.serialize() for parcel in parcels])
    
    elif request.method == 'POST':
        data = request.get_json()
        new_parcel = Parcel(
            sender=data['sender'],
            receiver=data['receiver'],
            weight=data['weight'],
            dimensions=data['dimensions'],
            status=data['status']
        )
        db.session.add(new_parcel)
        db.session.commit()
        return jsonify(new_parcel.serialize()), 201

@app.route('/parcels/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@cross_origin()
def parcel_detail(id):
    parcel = Parcel.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(parcel.serialize())
    
    elif request.method == 'PATCH':
        data = request.get_json()
        if 'sender' in data:
            parcel.sender = data['sender']
        if 'receiver' in data:
            parcel.receiver = data['receiver']
        if 'weight' in data:
            parcel.weight = data['weight']
        if 'dimensions' in data:
            parcel.dimensions = data['dimensions']
        if 'status' in data:
            parcel.status = data['status']
        db.session.commit()
        return jsonify(parcel.serialize())
    
    elif request.method == 'DELETE':
        db.session.delete(parcel)
        db.session.commit()
        return '', 204

@app.route('/admins', methods=['GET', 'POST'])
@cross_origin()
def admins():
    if request.method == 'GET':
        admins = Admin.query.all()
        return jsonify([admin.serialize() for admin in admins])
    
    elif request.method == 'POST':
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'])
        new_admin = Admin(
            username=data['username'],
            password=hashed_password,
            email=data['email']
        )
        db.session.add(new_admin)
        db.session.commit()
        return jsonify(new_admin.serialize()), 201

@app.route('/admins/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@cross_origin()
def admin_detail(id):
    admin = Admin.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(admin.serialize())
    
    elif request.method == 'PATCH':
        data = request.get_json()
        if 'username' in data:
            admin.username = data['username']
        if 'email' in data:
            admin.email = data['email']
        if 'password' in data:
            admin.password = generate_password_hash(data['password'])
        db.session.commit()
        return jsonify(admin.serialize())
    
    elif request.method == 'DELETE':
        db.session.delete(admin)
        db.session.commit()
        return '', 204

@app.route('/delivery_histories', methods=['GET', 'POST'])
@cross_origin()
def delivery_histories():
    if request.method == 'GET':
        histories = DeliveryHistory.query.all()
        return jsonify([history.serialize() for history in histories])
    
    elif request.method == 'POST':
        data = request.get_json()
        new_history = DeliveryHistory(
            parcel_id=data['parcel_id'],
            driver_id=data['driver_id'],
            delivered_at=data['delivered_at']
        )
        db.session.add(new_history)
        db.session.commit()
        return jsonify(new_history.serialize()), 201

@app.route('/notifications', methods=['GET', 'POST'])
@cross_origin()
def notifications():
    if request.method == 'GET':
        notifications = Notification.query.all()
        return jsonify([notification.serialize() for notification in notifications])
    
    elif request.method == 'POST':
        data = request.get_json()
        new_notification = Notification(
            message=data['message'],
            user_id=data['user_id'],
            created_at=data.get('created_at')
        )
        db.session.add(new_notification)
        db.session.commit()
        return jsonify(new_notification.serialize()), 201

@app.route('/parcel_types', methods=['GET', 'POST'])
@cross_origin()
def parcel_types():
    if request.method == 'GET':
        parcel_types = ParcelType.query.all()
        return jsonify([parcel_type.serialize() for parcel_type in parcel_types])
    
    elif request.method == 'POST':
        data = request.get_json()
        new_parcel_type = ParcelType(
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(new_parcel_type)
        db.session.commit()
        return jsonify(new_parcel_type.serialize()), 201

@app.route('/drivers', methods=['GET', 'POST'])
@cross_origin()
def drivers():
    if request.method == 'GET':
        drivers = Driver.query.all()
        return jsonify([driver.serialize() for driver in drivers])
    
    elif request.method == 'POST':
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'])
        new_driver = Driver(
            name=data['name'],
            license_number=data['license_number'],
            phone=data['phone'],
            password=hashed_password
        )
        db.session.add(new_driver)
        db.session.commit()
        return jsonify(new_driver.serialize()), 201

@app.route('/drivers/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@cross_origin()
def driver_detail(id):
    driver = Driver.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(driver.serialize())
    
    elif request.method == 'PATCH':
        data = request.get_json()
        if 'name' in data:
            driver.name = data['name']
        if 'license_number' in data:
            driver.license_number = data['license_number']
        if 'phone' in data:
            driver.phone = data['phone']
        if 'password' in data:
            driver.password = generate_password_hash(data['password'])
        db.session.commit()
        return jsonify(driver.serialize())
    
    elif request.method == 'DELETE':
        db.session.delete(driver)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(debug=True)
