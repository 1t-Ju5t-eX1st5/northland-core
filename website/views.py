from flask import Blueprint, render_template, request, flash, jsonify, redirect
from flask_login import login_required, current_user
from .backend import esidata

views = Blueprint('views', __name__)
EsiData = esidata.EsiData()

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/wallet')
@login_required
def wallet():
    char_wallet = EsiData.get_character_wallet()
    corp_wallet_res = EsiData.get_corporation_wallet()
    corp_wallet = []
    try:
        for item in corp_wallet_res.data:
            div_balance = round(float(str(item['balance']) + "000"), 2)
            corp_wallet.append(f'{div_balance:,}')
    except TypeError:
        flash('There is an error getting corporation wallet information', category='error')
        return render_template('wallet.html', char_wallet=char_wallet, corp_wallet_error=True)
    return render_template('wallet.html', char_wallet=char_wallet, corp_wallet=corp_wallet)

@views.route('/about')
def about():
    return render_template('about.html')