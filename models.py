from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parcels = db.relationship('Parcel', back_populates='user', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')

    serialize_rules = ('-parcels.user', '-notifications.user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Parcel(db.Model, SerializerMixin):
    __tablename__ = 'parcels'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
    weight = db.Column(db.Float, nullable=False)
    pickup_address = db.Column(db.String(255), nullable=False)
    pickup_lat = db.Column(db.Float, nullable=False)
    pickup_lng = db.Column(db.Float, nullable=False)
    destination_address = db.Column(db.String(255), nullable=False)
    destination_lat = db.Column(db.Float, nullable=False)
    destination_lng = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    present_location = db.Column(db.String(255))
    present_location_lat = db.Column(db.Float)
    present_location_lng = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='parcels')
    driver = db.relationship('Driver', back_populates='parcels')
    delivery_history = db.relationship('DeliveryHistory', back_populates='parcel', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='parcel', cascade='all, delete-orphan')

    serialize_rules = ('-user.parcels', '-driver.parcels', '-delivery_history.parcel', '-notifications.parcel')

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'driver_id': self.driver_id,
            'weight': self.weight,
            'pickup_address': self.pickup_address,
            'pickup_lat': self.pickup_lat,
            'pickup_lng': self.pickup_lng,
            'destination_address': self.destination_address,
            'destination_lat': self.destination_lat,
            'destination_lng': self.destination_lng,
            'status': self.status,
            'present_location': self.present_location,
            'present_location_lat': self.present_location_lat,
            'present_location_lng': self.present_location_lng,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Admin(db.Model, SerializerMixin):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class DeliveryHistory(db.Model, SerializerMixin):
    __tablename__ = 'delivery_history'

    id = db.Column(db.Integer, primary_key=True)
    parcel_id = db.Column(db.Integer, db.ForeignKey('parcels.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    location_lat = db.Column(db.Float, nullable=False)
    location_lng = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    parcel = db.relationship('Parcel', back_populates='delivery_history')

    serialize_rules = ('-parcel.delivery_history',)

    def serialize(self):
        return {
            'id': self.id,
            'parcel_id': self.parcel_id,
            'status': self.status,
            'location': self.location,
            'location_lat': self.location_lat,
            'location_lng': self.location_lng,
            'updated_at': self.updated_at.isoformat()
        }

class Notification(db.Model, SerializerMixin):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parcel_id = db.Column(db.Integer, db.ForeignKey('parcels.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')
    parcel = db.relationship('Parcel', back_populates='notifications')

    serialize_rules = ('-user.notifications', '-parcel.notifications')

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'parcel_id': self.parcel_id,
            'message': self.message,
            'sent_at': self.sent_at.isoformat()
        }

class ParcelType(db.Model, SerializerMixin):
    __tablename__ = 'parcel_types'

    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(255), nullable=False)
    weight_range = db.Column(db.Float, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'type_name': self.type_name,
            'weight_range': self.weight_range,
            'price': self.price
        }

class Driver(db.Model, SerializerMixin):
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

    parcels = db.relationship('Parcel', back_populates='driver')

    serialize_rules = ('-parcels.driver',)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number
        }
