from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

import time

class Note(db.Model):
    # Database entry template for a note
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))   # Column contains data from the class User (foreign relationship)
    


class User(db.Model, UserMixin):
    # Database entry template for a user account
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note') # Every time the user creates a new note, add its ID to the user's list
    
    """
    def is_active(self):
        return True
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id
    """

class Player(db.Model, UserMixin):
    character_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    character_name = db.Column(db.String(200), unique=True)
    character_owner_hash = db.Column(db.String(225))
    character_corp = db.Column(db.String(500))
    
    # SSO tokens and stuff, I guess...
    access_token = db.Column(db.String(4096))
    access_token_expire = db.Column(db.DateTime())
    refresh_token = db.Column(db.String(100))

    def get_id(self):
        # Helper function to return the character ID for esiapp, also required for Flask-Login (I think...)
        return self.character_id
    
    def get_sso_data(self):
        # Helper function to return token data to esisecurity, API-style :P
        # I kinda copied this...
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_in': (self.access_token_expire - datetime.utcnow()).total_seconds()
        }
    
    def update_token(self, token_response):
        # Helper function to update token data from SSO response
        # ... and this :P
        self.access_token = token_response['access_token']
        self.access_token_expire = datetime.fromtimestamp(
            time.time() + token_response['expires_in'],
        )
        if 'refresh_token' in token_response:
            self.refresh_token = token_response['refresh_token']