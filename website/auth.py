from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from . import db
from .models import User
from .backend import esidata
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user, current_user

auth = Blueprint('auth', __name__)
EsiData = esidata.EsiData()

"""
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('User does not exist', category='error')

    return render_template("login.html", user=current_user)
"""

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
    
    res = EsiData.authentication(True, code)
    print(res)
    if res:
        return redirect(url_for('views.home'))
    else:
        flash('EVE ESI SSO Login failed!', category='error')
    
    # Now that we've been successfully authenticated, lets redirect the user back to the home page and let the backend do the work

@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        first_name = request.form.get('first-name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('This email is already in use', category='error')
        elif len(email) < 4:
            flash('Email must be longer than 4 characters', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 7:
            flash('Password length must not be shorter than 7 characters', category='error')
        else:
            # add user to the database
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            # login_user(user) --- original code
            login_user(new_user) # correct code
            flash('Account created successfully!', category='success')
            return redirect(url_for('views.home'))

    elif request.method == "GET":
        pass
    else:
        pass

    return render_template("signup.html", user=current_user)