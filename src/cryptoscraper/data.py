from datetime import timedelta

from requests import Session
from _datetime import datetime

import cryptoscraper.utils as utils
import cryptoscraper.database.database as database
from cryptoscraper import parser


"""
CMCListing: the class to get semi-constant data (available coins, categories of coins, coins per category).
    Uses the key for the CoinMarketCap API.

CMCLatest: the class to get latest data information.
    Uses the key for the CoinMarketCap API.

CMCHistorical: the class to get historical information.
    Does not use the key for the CoinMarketCap API. Information is retrieved through web scraping.
"""


class CMC:
    """
    CMC: the parent class for every class that retrieves and manages data from the Web or the DB.
        Creates a session to query the coinmarketcap server and sets the API-key to perform the queries.
        Documentation for the CMC API can be found at https://coinmarketcap.com/api/documentation/v1/
    """
    # Only contains the constructor to set the API_KEY param and initialize the session
    def __init__(self, token=utils.API_KEY):
        self.api_url = 'https://pro-api.coinmarketcap.com'
        self.headers = {'Accepts': 'application/json',
                        'X-CMC_PRO_API_KEY': token}
        self.session = Session()
        self.session.headers.update(self.headers)


class CMCListing(CMC):
    """
    CMCListing: the class to get semi-constant data (available coins, categories of coins, coins per category).
        Uses the key for the CoinMarketCap API.
    """
    # Calls the parent constructor to retrieve session info
    def __init__(self):
        super().__init__()

    # Gets the list of coins
    def get_coins(self):
        # Retrieve data from DB
        db = database.DBGetter()
        data_list = db.get_coins()

        if data_list is not None:
            # Data are available in the DB
            return data_list

        # Data are not available in the DB
        res = self.update_coin_listing()
        return res

    # Retrieves the list of coins from CoinMarketCap
    def update_coin_listing(self):
        # Get data from API
        url = self.api_url + '/v1/cryptocurrency/map'
        r = self.session.get(url)

        # Get data
        try:
            json_data = r.json()
            utils.json_error_handling(json_data)

            # Parse json response
            jp = parser.JsonParser(json_data)
            data_list = jp.parse_all_coins()

            # Save data on db
            db = database.DBSetter(data_list)
            data_list = db.save_coins()

            return data_list

        except Exception as e:
            print("Cannot retrieve coins data")
            utils.error_msg(e)

    # Gets the list of coin categories
    def get_categories(self):
        # Retrieve data from db
        db = database.DBGetter()
        data_list = db.get_categories()

        if data_list is not None:
            return data_list

        # Update data on db
        data_list = self.update_category_listing()
        return data_list

    # Retrieves the list of coin categories from CoinMarketCap
    def update_category_listing(self):
        # Get data from API
        url = self.api_url + '/v1/cryptocurrency/categories'
        r = self.session.get(url)

        # Get data
        try:
            json_data = r.json()
            utils.json_error_handling(json_data)

            # Parse json response
            jp = parser.JsonParser(json_data)
            data_list = jp.parse_all_categories()

            # Save data on db
            db = database.DBSetter(data_list)
            data_list = db.save_categories()

            return data_list

        except Exception as e:
            print("Cannot retrieve categories data")
            utils.error_msg(e)

    # Gets the list of coins related to a given category
    def get_coins_for_category(self, name):
        # Retrieve data from db
        db = database.DBGetter()
        cat_id = db.get_category_id(name)
        if cat_id is None:
            return "'%s' not found. Try to update the database by calling 'update_category_listing()'" % name

        data_list = db.get_category_coins(cat_id)
        if (data_list is not None) and (len(data_list) != 0):
            return data_list

        # Update data on db
        data_list = self.update_coins_for_category(cat_id)
        return data_list

    # Retrieves the list of coins related to a given category from CoinMarketCap
    def update_coins_for_category(self, cat_id):
        # Get data from API
        url = self.api_url + '/v1/cryptocurrency/category'
        parameters = {'id': cat_id}
        r = self.session.get(url, params=parameters)

        # Get data
        try:
            json_data = r.json()
            utils.json_error_handling(json_data)

            # Parse json response
            jp = parser.JsonParser(json_data)
            data_list = jp.parse_category_coins(cat_id)

            # save data in db
            db = database.DBSetter(data_list)
            data_list = db.save_category_coins()

            return data_list

        except Exception as e:
            print("Cannot retrieve coins for category data")
            utils.error_msg(e)


class CMCLatest(CMC):
    """
    CMCLatest: the class to get the latest data related to price, market_cap and volumes for given coins.
        Uses scraping mechanisms to retrieve information without the API key.
    """
    def __init__(self, convert=utils.DEFAULT_CONVERT):
        super().__init__()
        self.convert = convert

    # Gets the latest data related to a given coin
    def get_latest_data(self, names=None):
        # Retrieve data from db
        db = database.DBGetter()
        id_list = []
        if names is not None:
            for name in names:
                c_id = db.get_coin_id(name)
                if c_id is None:
                    print("'%s' not found. Try to update the database by calling 'update_coin_listing()'" % name)
                    return None
                id_list.append(c_id)
        else:
            id_list = None

        price_list = db.get_latest_data(id_list, self.convert)
        if price_list is not None:
            return price_list

        # Get data from API
        price_list = self.update_latest_data(id_list)

        return price_list

    # Gets the latest data related to a given category
    def get_cat_coins_latest_data(self, cat_name):
        # Retrieve data
        cmc_listing = CMCListing()
        data_list = cmc_listing.get_coins_for_category(cat_name)

        id_list = []
        for item in data_list:
            id_list.append(item[0])
            
        db = database.DBGetter()
        price_list = db.get_latest_data(id_list, self.convert)

        if price_list is not None:
            return price_list

        # Get data from API
        price_list = self.update_latest_data(id_list)

        return price_list

    # Retrieves the latest data for a list of coins from CoinMarketCap
    def update_latest_data(self, id_list=None):
        # Download the latest data for every coin
        if id_list is None:
            url = self.api_url + '/v1/cryptocurrency/listings/latest'
            parameters = {'start': '1',
                          'limit': '200',
                          'convert': self.convert}

        # Download the latest data for some coins
        else:
            url = self.api_url + '/v1/cryptocurrency/quotes/latest'

            id_str = ""
            for i in range(len(id_list) - 1):
                id_str = id_str + str(id_list[i]) + ","
            id_str = id_str + str(id_list[len(id_list) - 1])
            parameters = {'id': id_str,
                          'convert': self.convert}

        # Download data
        r = self.session.get(url, params=parameters)
        data = r.json()

        # Parse json response
        jp = parser.JsonParser(data)
        data_list = jp.parse_latest_data(id_list, self.convert)

        # Save data in db
        db = database.DBSetter(data_list)
        data_list = db.save_latest_data(id_list, self.convert)

        return data_list

    # Get the conversion from a certain amount of a cryptocurrency to a given fiat
    def get_price_conversion(self, amount, name):
        data = self.get_latest_data([name])
        if data is None:
            return None

        result = data[0]
        str_res = str(amount) + " " + result[0] + " are " + format(float(result[2] * amount), '.2f') \
                  + " " + self.convert + ". Last update on " + utils.format_date(result[7]) + "."

        return str_res


class CMCHistorical:
    """
    CMCHistorical: the class to get the historical data related to price, market_cap and volumes for given coins.
        Uses scraping mechanisms to retrieve information without the API key.
    """
    # The constructor takes
    #   - the coin to retrieve information about
    #   - the time interval of said information
    #   - the order in which to get this information
    #   - the fiat used to show the prices
    def __init__(self, start_date=utils.DEFAULT_START, end_date=utils.DEFAULT_END, order_desc=False,
                 convert=utils.DEFAULT_CONVERT):
        # Arguments
        self.start_date = start_date

        if self.start_date == utils.DEFAULT_START:
            self.first_flag = True
        else:
            self.first_flag = False

        self.end_date = end_date
        self.order_desc = order_desc
        self.convert = convert

        # Fixed params
        self.scraping_url = 'https://web-api.coinmarketcap.com'

        # Result
        self.rows = []

    # Download historical data for the specified coin and time range
    def get_historical_data(self, coin):
        # Retrieve data from DB
        db = database.DBGetter()

        c_id = db.get_coin_id(coin)
        if c_id is None:
            print("'%s' not found. Try to update the database by calling 'update_coin_listing()'" % coin)
            return None

        data = db.get_historical_data(c_id, self.convert, self.start_date, self.end_date, self.order_desc)
        if data is not None:
            h_data = data
        else:
            h_data = self.update_historical_data(coin, c_id)

        return h_data

    def update_historical_data(self, coin, coin_id=None):
        if coin_id is None:
            coin_id = database.DBGetter().get_coin_id(coin)
            if coin_id is None:
                print("'%s' not found. Try to update the database by calling 'update_coin_listing()'" % coin)
                return None

        # Convert the date for the URL
        start = self.start_date - timedelta(days=1)  # Needed to get every date requested

        start_date_iso = start.isoformat()
        end_date_iso = self.end_date.isoformat()

        # Build URL
        url = self.scraping_url + "/v1/cryptocurrency/ohlcv/historical?convert={}&id={}&time_end={}&time_start={}" \
            .format(self.convert, coin_id, end_date_iso, start_date_iso)

        try:
            # Get data
            json_data = utils.get_url_data(url).json()
            utils.json_error_handling(json_data)

            # Parse data
            jp = parser.JsonParser(json_data)
            self.rows = jp.parse_historical_data(self.convert)

            # Update start and end with the data retrieved
            self.start_date = self.rows[0]['date']
            self.end_date = self.rows[-1]['date']

            # Order data in a descending way: from the last to the first
            if self.order_desc:
                self.rows.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))

            # Store downloaded data
            db = database.DBSetter(self.rows)
            res = db.save_historical_data(coin_id, self.convert, self.start_date, self.end_date, self.order_desc,
                                          self.first_flag)

            return res

        except Exception as e:
            print("Cannot retrieve historical data")
            utils.error_msg(e)
            return None
