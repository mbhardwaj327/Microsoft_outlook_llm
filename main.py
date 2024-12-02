from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from models import db, User
from flask_cors import CORS
from flask_migrate import Migrate
from ms_utils import MicrosoftGraphAPI
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://rag_microsoft_user:CogninestAI#123@173.249.0.212/rag_microsoft_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fjdfidjffjnfjfnnf'
app.config['JWT_SECRET_KEY'] = 'ijnijijiodjfffnn'


bcrypt = Bcrypt(app)
jwt = JWTManager(app)

migrate = Migrate(app, db)

# Initialize SQLAlchemy with the Flask app
db.init_app(app)


@app.route('/microsoft-login', methods=['POST'])
def microsoft_login():
    try:
        # Correct usage of request.json to access data
        data = request.json
        token = data.get("access_token")
        ms_refresh_token = data.get("refresh_token")
        email = data.get("mail")
        name = data.get("name")
        
        if not email:
            raise ValueError("Email address is required")
        
        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user if doesn't exist
            user = User(
                ms_id=data.get("id"),
                ms_access_token=token,
                ms_refresh_token=ms_refresh_token,
                name=name,
                email=email
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Update user's access token and other details if they exist
            user.ms_access_token = token
            user.ms_refresh_token = ms_refresh_token
            user.name = name
            db.session.commit()

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # response
        response_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "ms_access_token": user.ms_access_token,
                "profile_picture": user.profile_picture
            }
        }
        return jsonify(response_data), 201
    except Exception as err:
        return jsonify({"error": str(err)}), 400
    

@app.route('/google-login', methods=['POST'])
def google_login():
    try:
        # Extract user data from payload
        email = request.json.get("email")
        name = request.json.get("name")
        profile_picture = request.json.get("picture")
        token = request.json.get("access_token")

        if not email:
            return jsonify({"error": "Email is required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user if doesn't exist
            user = User(
                email=email,
                name=name,
                profile_picture=profile_picture,
                google_auth_token=token,
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Update existing user details
            user.name = name
            user.google_auth_token = token
            user.profile_picture = profile_picture
            db.session.commit()

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        # response
        response_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "profile_picture": user.profile_picture
            }
        }
        return jsonify(response_data), 201
    except Exception as err:
        return jsonify({"error": str(err)}), 400
    
    
@app.route('/fetch_microsoft_calendar_events', methods=['POST'])
@jwt_required()
def fetch_microsoft_calendar_events():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if user and user.ms_refresh_token:
        ms_obj = MicrosoftGraphAPI()
        all_events = ms_obj.get_all_calendar_events(user.ms_refresh_token)
        return jsonify(all_events), 200
    else:
        return jsonify({"error": "No Microsoft refresh token found", "isAuthenticated": False}), 403


if __name__ == '__main__':
    app.run(debug=True)
