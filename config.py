import os
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask import request, make_response, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
load_dotenv()
# Load environment variables from a .env file


app = Flask(__name__)
CORS(app)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

""" app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sendit.db' """
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')
# # Configure Bcrypt
# app.config['BCRYPT_LOG_ROUNDS'] = 12

# # Configure secret key


# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = (
    os.getenv("MAIL_DEFAULT_SENDER_NAME"),
    os.getenv("MAIL_DEFAULT_SENDER_EMAIL")
)

# Initialize extensions
db = SQLAlchemy()

migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)

db.init_app(app)
# Swagger UI setup
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
API_URL = '/static/swagger.json'  # URL for the Swagger JSON file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Test application"}
)
app.register_blueprint(swaggerui_blueprint)

# Add any additional configuration or initialization as needed

# Ensure to return the Flask app instance for running the app elsewhere
# def create_app():
#     return app
