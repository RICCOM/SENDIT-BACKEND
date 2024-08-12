from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Parcel, Admin, DeliveryHistory, Notification, ParcelType, Driver, Contact, Review
import os
from dotenv import load_dotenv

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
    username = data.get('username')
    password = data.get('password')
    user = authenticate_user(username, password)
    if user:
        access_token = create_access_token(identity={"email": user.email, "role": user.role})
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/users/signup', methods=['POST'])
@cross_origin()
def user_signup():
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'msg': 'All fields are required'}), 400

    # Check if the user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'Email already in use'}), 400
    
    # Create a new user
    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'User created successfully'}), 201


@app.route('/api/revenue', methods=['GET'])
@cross_origin()
@jwt_required()
def get_revenue():
    # For demonstration purposes, we return static data. Replace with your actual logic.
    revenue_data = [
        {"month": "January", "revenue": 12000},
        {"month": "February", "revenue": 19000},
        {"month": "March", "revenue": 30000},
        {"month": "April", "revenue": 50000},
        {"month": "May", "revenue": 20000},
        {"month": "June", "revenue": 30000},
        {"month": "July", "revenue": 70000},
    ]
    return jsonify(revenue_data), 200

@app.route('/api/contact', methods=['POST'])
@cross_origin()
def submit_contact():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject')
    message = data.get('message')

    if not all([name, email, subject, message]):
        return jsonify({'msg': 'All fields are required'}), 400

    new_contact = Contact(
        name=name,
        email=email,
        subject=subject,
        message=message
    )

    db.session.add(new_contact)
    db.session.commit()

    return jsonify({'msg': 'Your message has been received'}), 201

@app.route('/api/reviews', methods=['POST'])
@cross_origin()
@jwt_required()
def submit_review():
    data = request.get_json()
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()

    if not user:
        return jsonify({'msg': 'User not found'}), 404

    parcel_id = data.get('parcel_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not all([parcel_id, rating, comment]):
        return jsonify({'msg': 'All fields are required'}), 400

    new_review = Review(
        user_id=user.id,
        parcel_id=parcel_id,
        rating=rating,
        comment=comment
    )

    db.session.add(new_review)
    db.session.commit()

    return jsonify(new_review.serialize()), 201

@app.route('/api/parcels', methods=['GET'])
@cross_origin()
@jwt_required()
def get_parcels():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()

    if not user:
        return jsonify({'msg': 'User not found'}), 404

    parcels = Parcel.query.filter_by(user_id=user.id).all()
    return jsonify([parcel.serialize() for parcel in parcels]), 200

@app.route('/api/notifications', methods=['GET'])
@cross_origin()
@jwt_required()
def get_notifications():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()

    if not user:
        return jsonify({'msg': 'User not found'}), 404

    notifications = Notification.query.filter_by(user_id=user.id).all()
    return jsonify([notification.serialize() for notification in notifications]), 200

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
