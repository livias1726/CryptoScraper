from pprint import pp

from src.cryptomarket.Latest import CMCLatest
from src.cryptomarket.Listing import CMCListing
from src.database import database

# cmc = CMCListing()
# pp(cmc.get_coins()) (OK)
# pp(cmc.get_categories())
# pp(cmc.get_coins_for_category('AI & Big Data'))


# cmc = CMCLatest()
# pp(cmc.get_latest_data(['ethereum', 'bitcoin', 'cardano'], 'EUR')) (OK)
# pp(cmc.get_latest_data(None, 'USD')) (OK)
# pp(cmc.update_latest_data(None, 'USD')) (OK)
# pp(cmc.get_price_conversion(20, 'cardano', 'EUR')) (OK)

# db = database.DB()
# db.delete_table('latest_data')
