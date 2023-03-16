from flask import Blueprint, request, flash, redirect, url_for, session
from .backend import esidata
from flask_login import login_required, logout_user

auth = Blueprint('auth', __name__)
EsiData = esidata.EsiData()

@auth.route('/login')
def login():
    token = EsiData.generate_state()
    session['token'] = token
    return redirect(EsiData.generate_url(token))
    
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    # Security check to prevent CSRF attacks
    session_token = session.pop('token', None)
    if session_token is None or state is None or state != session_token:
        return "Login EVE Online SSO failed: Session Token Mismatch", 403
    
    #Now that the session has been checked to be legit, pass the 
    #code through the authentication function to authorize us
    res = EsiData.authentication(code)
    print(res)
    if res:
        # Hmm, looks like we've been authenticated, lets go home
        return redirect(url_for('views.home'))
    else:
        # Oops...
        flash('EVE ESI SSO Login failed!', category='error')