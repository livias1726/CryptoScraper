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

cmc = CMCHistorical()
cmc.update_historical_data('bitcoin')
"""

# LIST INFO
"""
cmc = CMCListing()
print(tabulate(cmc.get_coins(), headers=["ID", "NAME", "SYMBOL"]))
print(tabulate(cmc.get_categories(), headers=["NAME", "NUMBER OF TOKENS", "MARKET CAP", "VOLUME"]))
print(tabulate(cmc.get_coins_for_category('Cybersecurity'), headers=["ID", "NAME"]))
"""

"""
cmc = CMCLatest('USD')
print(tabulate(cmc.get_latest_data(['ethereum', 'bitcoin', 'cardano']), headers=["NAME", "CURRENCY", "PRICE", 
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
print(tabulate(cmc.get_historical_data('ethereum'), headers=["COIN", "DATE", "CURRENCY", "OPENING", "HIGHEST", "LOWEST",
                                                             "CLOSE", "VOLUME", "MARKET CAP"]))
"""


# SHOW INFO
g = Graph('bitcoin', 'close', 'y')
# g.show_observable()
g.show_coins_pairing({'ethereum'})
# g.show_obs_pairing({'open'})
# g.show_moving_average(200, True)

