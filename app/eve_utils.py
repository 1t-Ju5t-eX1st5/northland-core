from flask import Blueprint, render_template, request, flash, jsonify, redirect
from flask_login import login_required, current_user
from .backend import esidata

eve_utils = Blueprint('eve_utils', __name__)
EsiData = esidata.EsiData()

@eve_utils.route('/wallet')
@login_required
def wallet():
    char_wallet = EsiData.get_wallet_data("character")
    corp_wallet_res = EsiData.get_wallet_data("corporation")
    corp_wallet = []
    try:
        for item in corp_wallet_res.data:
            div_balance = round(float(str(item['balance']) + "000"), 2)
            corp_wallet.append(f'{div_balance:,}')
    except TypeError:
        flash('There is an error getting corporation wallet information', category='error')
        return render_template('wallet.html', char_wallet=char_wallet, corp_wallet_error=True)
    return render_template('wallet.html', char_wallet=char_wallet, corp_wallet=corp_wallet)


@eve_utils.route('/contracts', methods=['POST', 'GET'])
@login_required
def contracts():
    if request.method == "POST":
        contract_recipient = request.form['contract_recipient']
        contract_type = request.form['contract_type']
        contract_data = EsiData.get_contract_data(contract_recipient, contract_type)
        return render_template('contracts.html', contract_data=f"{contract_recipient} + {contract_type}")
    else:
        return render_template('contracts.html')