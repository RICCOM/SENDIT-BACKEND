# app.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Parcel, Admin, DeliveryHistory, Notification, ParcelType, Driver
import os
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurations for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Utility Functions
def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

# Routes

@app.route('/parcels/book', methods=['POST'])
@cross_origin()
@jwt_required()
def book_parcel():
    data = request.get_json()
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()

    if not user:
        return jsonify({'msg': 'User not found'}), 404

    new_parcel = Parcel(
        user_id=user.id,
        weight=data['weight'],
        pickup_address=data['pickup_address'],
        pickup_lat=data['pickup_lat'],
        pickup_lng=data['pickup_lng'],
        destination_address=data['destination_address'],
        destination_lat=data['destination_lat'],
        destination_lng=data['destination_lng'],
        status='Pending',
        present_location=data['pickup_address'],
        present_location_lat=data['pickup_lat'],
        present_location_lng=data['pickup_lng'],
    )
    db.session.add(new_parcel)
    db.session.commit()

    # Send a notification about the parcel booking
    notification = Notification(
        user_id=user.id,
        parcel_id=new_parcel.id,
        message=f'Parcel booked for delivery to {data["destination_address"]}',
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify(new_parcel.serialize()), 201

@app.route('/delivery_histories', methods=['GET'])
@cross_origin()
@jwt_required()
def delivery_histories():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()

    if not user:
        return jsonify({'msg': 'User not found'}), 404

    histories = DeliveryHistory.query.join(Parcel).filter(Parcel.user_id == user.id).all()
    return jsonify([history.serialize() for history in histories]), 200

@app.route('/users/login', methods=['POST'])
@cross_origin()
def user_login():
    data = request.get_json()
    print(f"Login attempt with data: {data}")  # Debugging statement
    username = data.get('username')
    password = data.get('password')
    user = authenticate_user(username, password)
    if user:
        access_token = create_access_token(identity={"email": user.email, "role": "user"})
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid username or password'}), 401

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
