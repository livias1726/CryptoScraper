from pprint import pp

from src.cryptomarket.Latest import CMCLatest
from src.cryptomarket.Listing import CMCListing
from src.database import database

# db = database.DB()
# db.delete_table('category_coins')

# cmc = CMCListing()
# pp(cmc.get_coins()) (OK)
# pp(cmc.get_categories()) (OK)
# pp(cmc.update_category_listing()) (OK)
# pp(cmc.get_coins_for_category('Cybersecurity')) (OK)


cmc = CMCLatest()
# pp(cmc.get_latest_data(['ethereum', 'bitcoin', 'cardano'], 'EUR')) (OK)
# pp(cmc.get_latest_data(None, 'USD')) (OK)
# pp(cmc.update_latest_data(None, 'USD')) (OK)
# pp(cmc.get_price_conversion(20, 'cardano', 'EUR')) (OK)
pp(cmc.get_cat_coins_latest_data('Cybersecurity', 'USD'))
