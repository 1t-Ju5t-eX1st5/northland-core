"""from app.backend import esidata
esidata_class = esidata.EsiData()

esidata_class.get_corporation_wallet_transactions(3)"""

with open('esi-scopes.txt') as f:
    scopes = [line.strip() for line in f]

print(scopes)
