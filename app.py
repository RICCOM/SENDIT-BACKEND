from models import User, Parcel, Admin, Driver
from config import app, Resource, api, make_response, request, db
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, current_user, jwt_required, JWTManager


from flask import Flask, jsonify
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail
# Configure JWT

app.config["JWT_SECRET_KEY"] = "b'Y\xf1Xz\x01\xad|eQ\x80t \xca\x1a\x10K'"
app.config['JWT_TOKEN_LOCATION'] = ['headers']
jwt = JWTManager(app)

CORS(app, resources={r"/*": {"origins": [
    "http://localhost:3000",
    # "https://spacehub2.netlify.app"
]}})
mail = Mail(app)

# Serializer for email verification
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@jwt.user_identity_loader
def user_identity_lookup(user):
    return {"id": user.id, "role": user.__class__.__name__}

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user_id = identity["id"]
    role = identity["role"]
    
    if role == "User":
        return User.query.filter_by(id=user_id).one_or_none()
    elif role == "Admin":
        return Admin.query.filter_by(id=user_id).one_or_none()
    elif role == "Driver":
        return Driver.query.filter_by(id=user_id).one_or_none()
    else:
        return None

class SignUp(Resource):
    def post(self):
        token = request.json.get('token')
        data = request.get_json()
        name = data.get("full_name")
        password = data.get("password")
        phone_number = data.get("phone_number")

        try:
            email = serializer.loads(token, salt='email-invite', max_age=86400)  # 1-day expiration
        except:
            return make_response({'message': 'Invalid or expired token.'}, 400)

        user = User.query.filter_by(invitation_token=token).first() or Admin.query.filter_by(invitation_token=token).first()

        if not user:
            return make_response({'message': 'Invalid or expired token.'}, 400)

        try:
            user.username = name
            user.account_status = "active"
            user.phone_number = phone_number
            user.password_hash = password
                
            db.session.commit()

            access_token = create_access_token(identity=user)
            return make_response({"user": user.to_dict(), 'access_token': access_token}, 201)
        except Exception as e:
            return {"error": e.args}, 422

api.add_resource(SignUp, "/signup")

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        user_class = {"User": User, "Admin": Admin, "Driver": Driver}.get(role)
        if not user_class:
            return make_response({"error": "Invalid role"}, 400)

        user = user_class.query.filter_by(email=email).first()

        if user and user.verify_password(password):
            access_token = create_access_token(identity=user)
            return make_response({"user": user.to_dict(), "access_token": access_token}, 201)
        else:
            return make_response({"error": "Unauthorized"}, 401)

api.add_resource(Login, "/login")

class CheckSession(Resource):
    @jwt_required()
    def get(self):
        return make_response(current_user.to_dict(), 200)

api.add_resource(CheckSession, '/check_session', endpoint="check_session")

class GetParcelDetails(Resource):
    def get(self, parcel_id):
        parcel = Parcel.query.filter_by(id=parcel_id).first()
        if parcel:
            return make_response(parcel.to_dict(), 200)
        return make_response({"error": "Parcel not found"}, 404)

api.add_resource(GetParcelDetails, "/parcels/<int:parcel_id>")

class UpdateParcelStatus(Resource):
    def patch(self, parcel_id):
        data = request.get_json()
        parcel = Parcel.query.filter_by(id=parcel_id).first()
        if parcel:
            if "status" in data:
                parcel.status = data["status"]
            
            try:
                db.session.commit()
                return make_response(parcel.to_dict(), 200)
            except Exception as e:
                return make_response({"error": str(e)}, 500)
        return make_response({"error": "Parcel not found"}, 404)

api.add_resource(UpdateParcelStatus, "/updateParcel/<int:parcel_id>")

class InviteDriver(Resource):
    def post(self):
        driver_email = request.json.get('email')

        token = serializer.dumps(driver_email, salt='email-invite')

        driver = Driver.query.filter_by(email=driver_email).first()
        if driver:
            return make_response({"error": "Unauthorized"}, 401)

        if not driver:
            driver = Driver(email=driver_email)
            db.session.add(driver)

        driver.invitation_token = token
        driver.role = 'Driver'
        driver.account_status = 'pending'
        db.session.commit()

        invite_url = f"https://example.com/#/signup?token={token}"

        msg = Message('Driver Sign Up Invitation', recipients=[driver_email])
        msg.body = f"You've been invited to sign up as a driver. Please use the following link to sign up: {invite_url}"
        mail.send(msg)
        
        return make_response({'message': 'Invitation sent to driver!'}, 200)

api.add_resource(InviteDriver, "/inviteDriver")

class ValidateToken(Resource):
    def post(self):
        token = request.json.get('token')
        try:
            email = serializer.loads(token, salt='email-invite', max_age=86400)
        except:
            return jsonify({'valid': False, 'message': 'Invalid or expired token.'}), 400

        user = User.query.filter_by(invitation_token=token).first() or Admin.query.filter_by(invitation_token=token).first() or Driver.query.filter_by(invitation_token=token).first()
        if user:
            return make_response({'valid': True, 'email': user.email}, 200)
        else:
            return make_response({'valid': False, 'message': 'Invalid or expired token.'}, 400)

api.add_resource(ValidateToken, "/validate-token")

class GetAllUsers(Resource):
    def get(self):
        users = User.query.all()
        return make_response([user.to_dict() for user in users], 200)

api.add_resource(GetAllUsers, "/users")

if __name__ == "__main__":
    app.run(debug=True, port=5555)






# from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_cors import CORS, cross_origin
# import bcrypt
# from models import db, User, Parcel, Admin, DeliveryHistory, Notification, ParcelType, Driver
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# import os
# from flask_swagger_ui import get_swaggerui_blueprint
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "https://sendit-fe-ten.vercel.app/"}})  

# app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'c1e587280cfa3822807fbfff64062177d1eb2c7e57fb6b02d121283a6d3ca6d6')
# jwt = JWTManager(app)

# @app.route('/api/data', methods=['GET'])
# def get_data():
#     return {'message': 'Hello, World!'}

# SWAGGER_URL = '/api/docs'
# API_URL = "/static/swagger.json"

# swagger_ui_blueprint = get_swaggerui_blueprint(
#     SWAGGER_URL,
#     API_URL,
#     config={
#         'app_name': 'Access API'
#     }
# )
# app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.json.compact = False


# db.init_app(app)
# migrate = Migrate(app, db)

# def hash_password(password):
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# def check_password(hashed_password, plain_password):
#     return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# def authenticate_user(username, password):
#     user = User.query.filter_by(username=username).first()
#     if user and check_password(user.password, password):
#         return user
#     return None


# @app.route('/')
# def home():
#     return "<h1>SendIT Courier Service</h1>"

# @app.route('/users', methods=['GET', 'POST'])
# @cross_origin()
# @jwt_required()  # Protect this route with JWT
# def users():
#     if request.method == 'GET':
#         users = User.query.all()
#         return jsonify([user.serialize() for user in users])
    
#     elif request.method == 'POST':
#         data = request.get_json()
#         hashed_password = hash_password(data['password'])
#         new_user = User(
#             username=data['username'],
#             email=data['email'],
#             password=hashed_password,
#             phone=data.get('phone')
#         )
#         db.session.add(new_user)
#         db.session.commit()
#         return jsonify(new_user.serialize()), 201

# @app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
# @cross_origin()
# @jwt_required()  # Protect this route with JWT
# def user_detail(id):
#     user = User.query.get_or_404(id)
#     if request.method == 'GET':
#         return jsonify(user.serialize())
    
#     elif request.method == 'PATCH':
#         data = request.get_json()
#         if 'username' in data:
#             user.username = data['username']
#         if 'email' in data:
#             user.email = data['email']
#         if 'phone' in data:
#             user.phone = data['phone']
#         if 'password' in data:
#             user.password = hash_password(data['password'])
#         db.session.commit()
#         return jsonify(user.serialize())
    
#     elif request.method == 'DELETE':
#         db.session.delete(user)
#         db.session.commit()
#         return '', 204

# @app.route('/users/login', methods=['POST'])
# @cross_origin()
# def user_login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')
#     user = authenticate_user(username, password)
#     if user:
#         access_token = create_access_token(identity=user.id)
#         return jsonify({'access_token': access_token}), 200
#     return jsonify({'message': 'Invalid username or password'}), 401

# @app.route('/parcels', methods=['GET', 'POST'])
# @cross_origin()
# @jwt_required()  # Protect this route with JWT
# def parcels():
#     if request.method == 'GET':
#         parcels = Parcel.query.all()
#         return jsonify([parcel.serialize() for parcel in parcels])
    
#     elif request.method == 'POST':
#         data = request.get_json()
#         new_parcel = Parcel(
#             sender=data['sender'],
#             receiver=data['receiver'],
#             weight=data['weight'],
#             dimensions=data['dimensions'],
#             status=data['status']
#         )
#         db.session.add(new_parcel)
#         db.session.commit()
#         return jsonify(new_parcel.serialize()), 201

# @app.route('/parcels/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
# @cross_origin()
# @jwt_required()  # Protect this route with JWT
# def parcel_detail(id):
#     parcel = Parcel.query.get_or_404(id)
#     if request.method == 'GET':
#         return jsonify(parcel.serialize())
    
#     elif request.method == 'PATCH':
#         data = request.get_json()
#         if 'sender' in data:
#             parcel.sender = data['sender']
#         if 'receiver' in data:
#             parcel.receiver = data['receiver']
#         if 'weight' in data:
#             parcel.weight = data['weight']
#         if 'dimensions' in data:
#             parcel.dimensions = data['dimensions']
#         if 'status' in data:
#             parcel.status = data['status']
#         db.session.commit()
#         return jsonify(parcel.serialize())
    
#     elif request.method == 'DELETE':
#         db.session.delete(parcel)
#         db.session.commit()
#         return '', 204

# @app.route('/admins', methods=['GET', 'POST'])
# @cross_origin()
# @jwt_required()  # Protect this route with JWT
# def admins():
#     if request.method == 'GET':
#         admins = Admin.query.all()
#         return jsonify([admin.serialize() for admin in admins])
    
#     elif request.method == 'POST':
#         data = request.get_json()
#         hashed_password = hash_password(data['password'])
#         new_admin = Admin(
#             username=data['username'],
#             password=hashed_password,
#             email=data['email']
#         )
#         db.session.add(new_admin)
#         db.session.commit()
#         return jsonify(new_admin.serialize()), 201

# @app.route('/admins/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
# @cross_origin()
# @jwt_required()  # Protect this route with JWT
# def admin_detail(id):
#     admin = Admin.query.get_or_404(id)
#     if request.method == 'GET':
#         return jsonify(admin.serialize())
    
#     elif request.method == 'PATCH':
#         data = request.get_json()
#         if 'username' in data:
#             admin.username = data['username']
#         if 'email' in data:
#             admin.email = data['email']
#         if 'password' in data:
#             admin.password = hash_password(data['password'])
#         db.session.commit()
#         return jsonify(admin.serialize())
    
#     elif request.method == 'DELETE':
#         db.session.delete(admin)
#         db.session.commit()
#         return '', 204

# @app.route('/delivery_histories', methods=['GET', 'POST'])
# @cross_origin()
# @jwt_required()  # Protect this route with JWT
# def delivery_histories():
#     if request.method == 'GET':
#         histories = DeliveryHistory.query.all()
#         return jsonify([history.serialize() for history in histories])
    
#     elif request.method == 'POST':
#         data = request.get_json()
#         new_history = DeliveryHistory(
#             parcel_id=data['parcel_id'],
#             driver_id=data['driver_id'],
#             delivered_at=data['delivered_at']
#         )
#         db.session.add(new_history)
#         db.session.commit()
#         return jsonify(new_history.serialize()), 201

# @app.route('/notifications', methods=['GET', 'POST'])
# @cross_origin()
# @jwt_required()  # Protect this route with JWT
# def notifications():
#     if request.method == 'GET':
#         notifications = Notification.query.all()
#         return jsonify([notification.serialize() for notification in notifications])
    
#     elif request.method == 'POST':
#         data = request.get_json()
#         new_notification = Notification(
#             message=data['message'],
#             user_id=data['user_id'],
#             created_at=data.get('created_at')
#         )
#         db.session.add(new_notification)
#         db.session.commit()
#         return jsonify(new_notification.serialize()), 201

# @app.route('/parcel_types', methods=['GET', 'POST'])
# @cross_origin()
# @jwt_required()  # Protect this route with JWT
# def parcel_types():
#     if request.method == 'GET':
#         parcel_types = ParcelType.query.all()
#         return jsonify([parcel_type.serialize() for parcel_type in parcel_types])
    
#     elif request.method == 'POST':
#         data = request.get_json()
#         new_parcel_type = ParcelType(
#             name=data['name'],
#             description=data.get('description')
#         )
#         db.session.add(new_parcel_type)
#         db.session.commit()
#         return jsonify(new_parcel_type.serialize()), 201

# @app.route('/drivers', methods=['GET', 'POST'])
# @cross_origin()
# @jwt_required()  # Protect this route with JWT
# def drivers():
#     if request.method == 'GET':
#         drivers = Driver.query.all()
#         return jsonify([driver.serialize() for driver in drivers])
    
#     elif request.method == 'POST':
#         data = request.get_json()
#         new_driver = Driver(
#             name=data['name'],
#             phone=data['phone'],
#             email=data['email']
#         )
#         db.session.add(new_driver)
#         db.session.commit()
#         return jsonify(new_driver.serialize()), 201

# if __name__ == '__main__':
#     app.run(debug=True)
