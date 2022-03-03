from requests import Session
from _datetime import datetime
import src.cryptomarket.utils as utils
import src.database.database as database
from src.cryptomarket import parser


# https://coinmarketcap.com/api/documentation/v1/
class CMC:
    def __init__(self, token=utils.API_KEY):
        self.api_url = 'https://pro-api.coinmarketcap.com'
        self.headers = {'Accepts': 'application/json',
                        'X-CMC_PRO_API_KEY': token}
        self.session = Session()
        self.session.headers.update(self.headers)


class CMCListing(CMC):

    def __init__(self):
        super().__init__()

    def get_coins(self):
        # Retrieve data from db
        db = database.DBGetter()
        data_list = db.get_coins()
        if data_list is not None:
            return data_list

        # Update data on db
        res = self.update_coin_listing()
        return res

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

    def get_categories(self):
        # Retrieve data from db
        db = database.DBGetter()
        data_list = db.get_categories()
        if data_list is not None:
            return data_list

        # Update data on db
        data_list = self.update_category_listing()
        return data_list

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

    def __init__(self, convert=utils.DEFAULT_CONVERT):
        super().__init__()
        self.convert = convert

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

    def update_latest_data(self, id_list):
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

        result = data[0][0]
        str_res = str(amount) + " " + result[0] + " are " + format(result[2] * amount, '.2f') \
                  + " " + self.convert + " (last update on " + utils.format_date(result[7]) + ")"

        return str_res


class CMCHistorical:

    def __init__(self, coin, start_date=utils.DEFAULT_START, end_date=utils.DEFAULT_END, order_desc=False,
                 convert=utils.DEFAULT_CONVERT):
        # Arguments
        self.coin = coin
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
        self.header = ('Coin', 'Date', 'Currency', 'Opening', 'Highest', 'Lowest', 'Volume', 'Market Cap')

        # Result
        self.rows = []

    # Download historical data for the specified coins and time range
    def get_historical_data(self):
        # Retrieve data from DB
        db = database.DBGetter()

        c_id = db.get_coin_id(self.coin)
        if c_id is None:
            print("'%s' not found. Try to update the database by calling 'update_coin_listing()'" % self.coin)
            return None

        data = db.get_historical_data(c_id, self.convert, self.start_date, self.end_date, self.order_desc)
        if data is not None:
            h_data = data
        else:
            res = self._download_historical_data(c_id)
            if res is None:
                return res

            # Store downloaded data
            db = database.DBSetter(res)
            h_data = db.save_historical_data(c_id, self.convert, self.start_date, self.end_date, self.order_desc,
                                             self.first_flag)

        h_data.insert(0, self.header)
        return h_data

    def _download_historical_data(self, coin_id):
        # Convert the date for the URL
        start_date_iso = self.start_date.isoformat()
        end_date_iso = self.end_date.isoformat()

        # Build URL
        url = self.scraping_url + "/v1/cryptocurrency/ohlcv/historical?convert={}&id={}&time_end={}&time_start={}" \
            .format(self.convert, coin_id, end_date_iso, start_date_iso)

        # Get data
        try:
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

            return self.rows

        except Exception as e:
            print("Cannot retrieve historical data")
            utils.error_msg(e)
            return None
