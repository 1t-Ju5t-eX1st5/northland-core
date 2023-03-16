# ESI related package imports (EsiPy)
from esipy.exceptions import APIException
from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity
from esipy.utils import generate_code_verifier

# Flask related package imports
from flask_login import login_user, current_user

# Custom package imports
from app.models import User
from app import db
from .esidata_exceptions import UnexpectedDataException

# Built-in package imports
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
        scopes = []
        with open('esi-scopes.txt') as f:
            scopes = [line.strip() for line in f]
        print(scopes)
        eve_sso_auth_url = self.security.get_auth_uri(
            state=token,
            scopes=["esi-contracts.read_corporation_contracts.v1", "esi-contracts.read_character_contracts.v1", "esi-wallet.read_character_wallet.v1", "esi-wallet.read_corporation_wallets.v1"]
        )
        return eve_sso_auth_url

    def authentication(self, code = ""):
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
        corporation_id_op = self.esiapp.op['get_characters_character_id'](
            character_id=character_data['sub'].split(':')[2]
        )
        # self.corporation_id = self.client.request(corporation_id_op).data['corporation_id']
        user.corporation_id = self.client.request(corporation_id_op).data['corporation_id']

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

    def get_wallet_data(self, wallet_type: str):
        # If current user is authenticated, get wallet content
        if current_user.is_authenticated:
            self.security.update_token(current_user.get_sso_data())
            if wallet_type == "character":
                op = self.esiapp.op['get_characters_character_id_wallet'](
                    character_id=current_user.character_id
                )
            elif wallet_type == "corporation":
                op = self.esiapp.op['get_corporations_corporation_id_wallets'](
                    corporation_id=current_user.corporation_id
                )
            wallet_data = self.client.request(op)
        return wallet_data

    def get_contract_data(self, contract_recipient: str, contract_status: str):
        expected_contract_recipient = "all/character/corporation"
        expected_contract_status = "all/outstanding/finished/expired"
        contract_data = []
        if current_user.is_authenticated:
            self.security.update_token(current_user.get_sso_data())
            if contract_recipient == "character":
                op = self.esiapp.op['get_characters_character_id_contracts'](
                    character_id=current_user.character_id
                )
                res = self.client.request(op).data
            elif contract_recipient == "corporation":
                op = self.esiapp.op['get_corporations_corporation_id_contracts'](
                    corporation_id=current_user.corporation_id
                )
                res = self.client.request(op).data
                for i in range(len(res)):
                    contract = res[i]
                    if contract['assignee_id'] == current_user.corporation_id:
                        contract_data.append(contract)
                    else:
                        pass
            else:
                raise UnexpectedDataException(expected_contract_recipient, contract_recipient)

            if len(contract_data) == 0:
                result = "No results found"
                return result
            
            if contract_status in ["outstanding", "finished", "expired"]:
                response = []
                for i in range(len(contract_data)):
                    current_array = contract_data[i]
                    if current_array['status'] == contract_status:
                        response.append(current_array)
                    else:
                        pass
                print(response)
                return response
            elif contract_status == "all":
                return contract_data
            else:
                raise UnexpectedDataException(expected_contract_status, contract_status)