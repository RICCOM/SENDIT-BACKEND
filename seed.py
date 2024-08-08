from datetime import datetime
from app import app, db
from models import User, Parcel, Admin, DeliveryHistory, Notification, ParcelType, Driver

def seed_database():
    # Create sample data
    users = [
        User(username='user1', email='user1@example.com', password_hash='hashedpassword1'),
        User(username='user2', email='user2@example.com', password_hash='hashedpassword2')
    ]

    admins = [
        Admin(username='admin1', email='admin1@example.com', password_hash='hashedpassword1')
    ]

    drivers = [
        Driver(name='Driver 1', phone_number='1234567890'),
        Driver(name='Driver 2', phone_number='0987654321')
    ]

    parcel_types = [
        ParcelType(type_name='Standard', weight_range=5.0, price=10),
        ParcelType(type_name='Express', weight_range=10.0, price=20)
    ]

    parcels = [
        Parcel(
            user_id=1,
            driver_id=1,
            weight=2.5,
            pickup_address='123 Main St',
            pickup_lat=40.7128,
            pickup_lng=-74.0060,
            destination_address='456 Elm St',
            destination_lat=40.7306,
            destination_lng=-73.9352,
            status='Pending'
        ),
        Parcel(
            user_id=2,
            driver_id=2,
            weight=7.0,
            pickup_address='789 Oak St',
            pickup_lat=40.748817,
            pickup_lng=-73.985428,
            destination_address='101 Pine St',
            destination_lat=40.7527,
            destination_lng=-73.9812,
            status='Shipped'
        )
    ]

    delivery_histories = [
        DeliveryHistory(
            parcel_id=1,
            status='Picked Up',
            location='123 Main St',
            location_lat=40.7128,
            location_lng=-74.0060
        ),
        DeliveryHistory(
            parcel_id=2,
            status='In Transit',
            location='789 Oak St',
            location_lat=40.748817,
            location_lng=-73.985428
        )
    ]

    notifications = [
        Notification(user_id=1, parcel_id=1, message='Your parcel has been picked up.'),
        Notification(user_id=2, parcel_id=2, message='Your parcel is in transit.')
    ]

    # Add and commit data to the database
    with app.app_context():
        db.create_all()  # Create tables if they do not exist
        db.session.add_all(users + admins + drivers + parcel_types + parcels + delivery_histories + notifications)
        db.session.commit()
        print("Database seeded successfully.")

if __name__ == '__main__':
    seed_database()
