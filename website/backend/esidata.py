from esipy.exceptions import APIException
from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity
from esipy.utils import generate_code_verifier

from flask_login import login_user, current_user

from website.models import User
from website import db

import json
import hashlib
import secrets

with open("dev_config.json") as f:
    config = json.load(f)
    app_config = config['application']

class EsiData():
    """
    Class designed to interface with the ESI database using the EsiPy library

    Requires authentication() and __init__() at minimum to work properly
    """

    def __init__(self):
        """
        Defines critical variables needed for the ESI client to work, including the client and security features
        """
        self.security = EsiSecurity(
            redirect_uri = app_config['callback'],
            client_id = app_config['client_id'],
            code_verifier = generate_code_verifier(),
            headers = app_config['headers']
        )
        self.client = EsiClient(
            headers = app_config['headers'],
            retry_requests = True,
            security = self.security
        )
        self.esiapp = EsiApp().get_latest_swagger
    def generate_state(self):
        """
        Generates a secure state for the EsiSecurity application to send requests to the ESI database
        """
        selection = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!;:*^%&#_-"
        result = ""
        for i in range(32):
            result += secrets.choice(selection)
        return hashlib.sha256(result.encode('utf-8')).hexdigest()
    
    def generate_url(self, token):
        """
        Generates the SSO url redirect to authenticate the user

        Arguments: 
        token: The state of the URL (random token recommended, use generate_state() to generate a random state ID)
        """
        eve_sso_auth_url = self.security.get_auth_uri(
            state=token,
            scopes=["esi-wallet.read_character_wallet.v1", "esi-wallet.read_corporation_wallets.v1"]
        )
        return eve_sso_auth_url

    def authentication(self, check_token = False, code = ""):
        """
        Interacts with the ESI database via the EsiPy and PySwagger libraries
        """
        # Get tokens using the code we retrieved earlier, and throw an error if the code doesnt work
        try:
            auth_response = self.security.auth(code)
        except APIException as e:
            return f'Login EVE Online SSO failed: {e}', 403
        
        # Now that we're logged in, grab the user's data from CCP's servers (or something...)
        character_data = self.security.verify()
        
        # Check in the database if the user exists, and if they arent create a new user account for them
        user = User.query.filter_by(character_id=character_data['sub'].split(':')[2]).first()
        if user == None:
            user = User()
            user.character_id = character_data['sub'].split(':')[2]
        
        user.character_owner_hash = character_data['owner']
        user.character_name = character_data['name']
        user.update_token(auth_response)
        character_corp_op = self.esiapp.op['get_characters_character_id'](
            character_id=character_data['sub'].split(':')[2]
        )
        # self.character_corp = self.client.request(character_corp_op).data['corporation_id']
        user.character_corp = self.client.request(character_corp_op).data['corporation_id']

        # New user created, now we add them to our database (I should really rename it...)
        try:
            db.session.merge(user)
            db.session.commit()
            login_user(user)
            print("Login success")
        except:
            # Whoops, something went wrong with the database, lets rewind our changes and log out the user
            db.session.rollback()
            print("Login failed")
        finally:
            print("Returning user")
            return user

    def get_corporation_wallet(self):
        corp_wallet = None
        
        # If current user is authenticated, get wallet content
        if current_user.is_authenticated:
            self.security.update_token(current_user.get_sso_data())
            op = self.esiapp.op['get_corporations_corporation_id_wallets'](
                corporation_id=current_user.character_corp
            )
            corp_wallet = self.client.request(op)
        return corp_wallet

    def get_character_wallet(self):
        char_wallet = None

        # If current user is authenticated, get wallet content
        if current_user.is_authenticated:
            self.security.update_token(current_user.get_sso_data())
            op = self.esiapp.op['get_characters_character_id_wallet'](
                character_id=current_user.character_id
            )
            char_wallet = self.client.request(op)
        return char_wallet
    
    def get_corporation_wallet_transactions(self, wallet_division=1):
        corp_transactions = None

        if current_user.is_authenticated:
            self.security.update_token(current_user.get_sso_data())
            op = self.esiapp.op['get_corporations_corporation_id_wallets_division_journal'](
                corporation_id=current_user.character_corp,
                division=wallet_division
            )
            corp_transactions = self.client.request(op)
        return corp_transactions