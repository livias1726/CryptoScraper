import datetime
import time
from pprint import pp

from src.cryptomarket import graphs
from src.cryptomarket.data import CMCHistorical
from src.database import database

# db = database.DBConnector()
# db.delete_table('historical_data')

# cmc = CMCListing()
# pp(cmc.get_coins())
# pp(cmc.get_categories())
# pp(cmc.update_category_listing())
# pp(cmc.get_coins_for_category('Cybersecurity'))

# cmc = CMCLatest()
# pp(cmc.get_latest_data(['ethereum', 'bitcoin', 'cardano'], 'EUR'))
# pp(cmc.get_latest_data(None, 'USD'))
# pp(cmc.update_latest_data(None, 'USD'))
# pp(cmc.get_price_conversion(20, 'cardano', 'EUR'))
# pp(cmc.get_cat_coins_latest_data('Cybersecurity', 'USD'))

# cmc = CMCHistorical('bitcoin')
# print(*cmc.get_historical_data(), sep='\n')

pp(graphs.show_openings())

