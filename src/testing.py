from tabulate import tabulate

from src.cryptomarket.data import CMCHistorical, CMC, CMCListing, CMCLatest
from src.cryptomarket.graphs import Graph
from src.database import database

db = database.DBConnector()

# UPDATE INFO
"""
cmc = CMCListing()
cmc.update_coin_listing()
cmc.update_category_listing()
cmc.update_category_listing()

cmc = CMCLatest()
cmc.update_latest_data()
"""
cmc = CMCHistorical()
cmc.update_historical_data('cardano')


# LIST INFO
"""
cmc = CMCListing()
print(tabulate(cmc.get_coins(), headers=["ID", "NAME", "SYMBOL"]))
print(tabulate(cmc.get_categories(), headers=["NAME", "NUMBER OF TOKENS", "MARKET CAP", "VOLUME"]))
print(tabulate(cmc.get_coins_for_category('Cybersecurity'), headers=["ID", "NAME"]))
"""

"""
cmc = CMCLatest()
print(tabulate(cmc.get_latest_data(['ethereum', 'bitcoin', 'litecoin']), headers=["NAME", "CURRENCY", "PRICE", 
                                                                                 "VOLUME (24H)", "VOLUME CHANGE (24H)", 
                                                                                 "PERCENT CHANGE (24H)", "MARKET CAP", 
                                                                                 "LAST UPDATE"]))

print(tabulate(cmc.get_latest_data(), headers=["NAME", "CURRENCY", "PRICE", "VOLUME (24H)", "VOLUME CHANGE (24H)", 
                                               "PERCENT CHANGE (24H)", "MARKET CAP", "LAST UPDATE"]))
print(cmc.get_price_conversion(20, 'cardano'))
print(tabulate(cmc.get_cat_coins_latest_data('Cybersecurity'), headers=["NAME", "CURRENCY", "PRICE", "VOLUME (24H)", 
                                                                        "VOLUME CHANGE (24H)", "PERCENT CHANGE (24H)", 
                                                                        "MARKET CAP", "LAST UPDATE"]))

cmc = CMCHistorical()
print(tabulate(cmc.get_historical_data('cardano'), headers=["COIN", "DATE", "CURRENCY", "OPENING", "HIGHEST", "LOWEST",
                                                             "CLOSE", "VOLUME", "MARKET CAP"]))
"""

# SHOW INFO
# g = Graph('bitcoin', 'high', 'd', '2020-08-06')
# g.show_observable()
# g.show_coins_pairing({'cardano'}, correlation=True)
# g.show_obs_pairing({'low'})
# g.show_sma([50, 100])
# g.show_ema([50, 100], 2)
# g.show_ma(100, 2)
# g.show_latest_pairing(['ethereum', 'litecoin'])
