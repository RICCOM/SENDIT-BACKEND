from datetime import datetime
from config import db, app, bcrypt
from models import User, Admin, Parcel, Driver

def seed_data():
    with app.app_context():
        # Clear existing data
        db.session.query(Parcel).delete()
        db.session.query(Driver).delete()
        db.session.query(Admin).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Create Users
        user1 = User(username="Justin", email="justin@gmail.com", phone_number="1234567890")
        user1.password_hash = "justinpassword"

        user2 = User(username="Grace", email="grace@gmail.com", phone_number="0987654321")
        user2.password_hash = "gracepassword"

        db.session.add_all([user1, user2])
        db.session.commit()

        # Create Admins
        admin1 = Admin(username="Joy", email="joy@gmail.com", phone_number="1122334455")
        admin1.password_hash = "joypassword"

        admin2 = Admin(username="Eric", email="eric@gmail.com", phone_number="5544332211")
        admin2.password_hash = "ericpassword"

        db.session.add_all([admin1, admin2])
        db.session.commit()

        # Create Drivers
        driver1 = Driver(username="driver_tony", email="tony@gmail.com", phone_number="6677889900", vehicle_type="Van")
        driver1.password_hash = "tonypassword"

        driver2 = Driver(username="driver_grace", email="grace@gmail.com", phone_number="9988776655", vehicle_type="Truck")
        driver2.password_hash = "gracepassword"

        db.session.add_all([driver1, driver2])
        db.session.commit()

        # Create Parcels
        parcel1 = Parcel(
            sender_address="123 Main St, New York, NY",
            receiver_address="456 Elm St, San Francisco, CA",
            weight=5.0,
            cost_per_kg=10.0,
            status="In Transit",
            user_id=user1.id,
            driver_id=driver1.id
        )

        parcel2 = Parcel(
            sender_address="789 Maple St, Los Angeles, CA",
            receiver_address="101 Pine St, Chicago, IL",
            weight=2.0,
            cost_per_kg=10.0,
            status="Delivered",
            user_id=user2.id,
            driver_id=driver2.id
        )

        parcel3 = Parcel(
            sender_address="234 Oak St, Miami, FL",
            receiver_address="567 Cedar St, Boston, MA",
            weight=3.5,
            cost_per_kg=10.0,
            status="Pending",
            user_id=user1.id,
            driver_id=driver1.id
        )

        db.session.add_all([parcel1, parcel2, parcel3])
        db.session.commit()

if __name__ == "__main__":
    seed_data()

# from datetime import datetime, timedelta
# from config import db, app, bcrypt
# from models import User, Admin, Parcel, Driver

# def seed_data():
#     with app.app_context():
#         # Clear existing data
#         db.session.query(Parcel).delete()
#         db.session.query(Driver).delete()
#         db.session.query(Admin).delete()
#         db.session.query(User).delete()
#         db.session.commit()

#         # Create Users
#         user1 = User(username="Justin", email="justin@gmail.com")
#         user1.password_hash = "justinpassword"

#         user2 = User(username="Grace", email="grace@gmail.com")
#         user2.password_hash = "gracepassword"

#         db.session.add_all([user1, user2])
#         db.session.commit()

#         # Create Admins
#         admin1 = Admin(username="Joy", email="joy@gmail.com", role="Admin")
#         admin1.password_hash = "joypassword"

#         admin2 = Admin(username="Eric", email="eric@gmail.com", role="Admin")
#         admin2.password_hash = "ericpassword"

#         db.session.add_all([admin1, admin2])
#         db.session.commit()

#         # Create Drivers
#         driver1 = Driver(username="driver_tony", email="tony@gmail.com")
#         driver1.password_hash = "tonypassword"

#         driver2 = Driver(username="driver_grace", email="grace@gmail.com")
#         driver2.password_hash = "gracepassword"

#         db.session.add_all([driver1, driver2])
#         db.session.commit()

#         # Create Parcels
#         parcel1 = Parcel(
#             description="Laptop delivery",
#             origin="New York",
#             destination="San Francisco",
#             weight=5.0,
#             delivery_status="In Transit",
#             user_id=user1.id,
#             driver_id=driver1.id
#         )

#         parcel2 = Parcel(
#             description="Book delivery",
#             origin="Los Angeles",
#             destination="Chicago",
#             weight=2.0,
#             delivery_status="Delivered",
#             user_id=user2.id,
#             driver_id=driver2.id
#         )

#         parcel3 = Parcel(
#             description="Clothing delivery",
#             origin="Miami",
#             destination="Boston",
#             weight=3.5,
#             delivery_status="Pending",
#             user_id=user1.id,
#             driver_id=driver1.id
#         )

#         db.session.add_all([parcel1, parcel2, parcel3])
#         db.session.commit()

# if __name__ == "__main__":
#     seed_data()
