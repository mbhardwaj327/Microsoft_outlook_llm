from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.mysql import LONGTEXT
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ms_access_token = db.Column(LONGTEXT, nullable=True) 
    ms_refresh_token = db.Column(LONGTEXT, nullable=True) 
    ms_id = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Hashed password
    google_auth_token = db.Column(LONGTEXT, nullable=True)   # Google auth token
    profile_picture = db.Column(db.String(255), nullable=True) 

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)