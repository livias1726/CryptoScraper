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
        db = database.Storage()
        data_list = db.get_coins()
        if data_list is not None:
            return data_list

        # Update data on db
        res = self.update_coin_listing()
        return res

    def get_categories(self):
        # Retrieve data from db
        db = database.Storage()
        data_list = db.get_categories()
        if data_list is not None:
            return data_list

        # Update data on db
        data_list = self.update_category_listing()
        return data_list

    def get_coins_for_category(self, name):
        # Retrieve data from db
        db = database.Storage()
        cat_id = db.get_category_id(name)
        if cat_id is None:
            return "'%s' not found. Try to update the database by calling 'update_category_listing()'" % name

        data_list = db.get_category_coins(cat_id)
        if (data_list is not None) and (len(data_list) != 0):
            return data_list

        # Update data on db
        data_list = self.update_coins_per_category(cat_id)
        return data_list

    def update_coin_listing(self):
        # Get data from API
        url = self.api_url + '/v1/cryptocurrency/map'
        r = self.session.get(url)
        data = r.json()

        # Parse json response
        jp = parser.Parser(data)
        data_list = jp.parse_all_coins()

        # Save data on db
        db = database.Storage()
        data_list = db.save_coins(data_list)

        return data_list

    def update_category_listing(self):
        # Get data from API
        url = self.api_url + '/v1/cryptocurrency/categories'
        r = self.session.get(url)
        data = r.json()

        # Parse json response
        jp = parser.Parser(data)
        data_list = jp.parse_all_categories()

        # Save data on db
        db = database.Storage()
        data_list = db.save_categories(data_list)

        return data_list

    def update_coins_per_category(self, cat_id):
        # Get data from API
        url = self.api_url + '/v1/cryptocurrency/category'
        parameters = {'id': cat_id}
        r = self.session.get(url, params=parameters)
        data = r.json()

        # Parse json response
        jp = parser.Parser(data)
        data_list = jp.parse_category_coins(cat_id)

        # save data in db
        db = database.Storage()
        data_list = db.save_category_coins(data_list)
        return data_list


class CMCLatest(CMC):

    def __init__(self):
        super().__init__()

    def get_latest_data(self, names, convert):
        # Retrieve data from db
        db = database.Storage()
        id_list = []
        if names is not None:
            for name in names:
                c_id = db.get_coin_id(name)
                if c_id is None:
                    print("'%s' not found. Try to update the database by calling 'update_coin_listing()'" % name)
                    return None
                id_list.append(c_id)

            price_list = db.get_latest_data(id_list, convert)
        else:
            id_list = None
            price_list = db.get_latest_data(id_list, convert)

        if price_list is not None:
            return price_list

        # Get data from API
        price_list = self.update_latest_data(id_list, convert)

        return price_list

    def get_cat_coins_latest_data(self, cat_name, convert):
        # Retrieve data
        db = database.Storage()

        cmc_listing = CMCListing()
        data_list = cmc_listing.get_coins_for_category(cat_name)

        id_list = []
        for item in data_list:
            id_list.append(item[0])
        price_list = db.get_latest_data(id_list, convert)

        if price_list is not None:
            return price_list

        # Get data from API
        price_list = self.update_latest_data(id_list, convert)

        return price_list

    # Get the conversion from a certain amount of a cryptocurrency to a given fiat
    def get_price_conversion(self, amount, name, convert):
        data = self.get_latest_data([name], convert)
        if data is None:
            return None

        result = data[0][0]
        str_res = str(amount) + " " + result[0] + " are " + format(result[2] * amount, '.2f') \
                  + " " + convert + " (last update on " + utils.format_date(result[7]) + ")"

        return str_res

    def update_latest_data(self, id_list, convert):
        db = database.Storage()
        if id_list is None:
            url = self.api_url + '/v1/cryptocurrency/listings/latest'
            parameters = {'start': '1',
                          'limit': '200',
                          'convert': convert}
            r = self.session.get(url, params=parameters)
            data = r.json()
        else:
            url = self.api_url + '/v1/cryptocurrency/quotes/latest'

            id_str = ""
            for i in range(len(id_list) - 1):
                id_str = id_str + str(id_list[i]) + ","
            id_str = id_str + str(id_list[len(id_list) - 1])
            parameters = {'id': id_str,
                          'convert': convert}

            r = self.session.get(url, params=parameters)
            data = r.json()

        # Parse json response
        jp = parser.Parser(data)
        data_list = jp.parse_latest_data(id_list, convert)

        # Save data in db
        data_list = db.save_latest_data(data_list, id_list, convert)

        return data_list


class CMCHistorical:

    def __init__(
            self,
            coin,
            start_date=None,
            end_date=None,
            all_time=False,
            order_ascending=False,
            convert=utils.DEFAULT_CONVERT
    ):
        self.coin = coin
        self.start_date = start_date
        self.end_date = end_date
        self.all_time = bool(all_time)
        self.order_ascending = order_ascending
        self.convert = convert
        self.headers = ["Date", "Open", "High", "Low", "Close", "Volume", "Market Cap"]
        self.rows = []
        self.scraping_url = 'https://web-api.coinmarketcap.com'

        if not (self.start_date and self.end_date):
            self.all_time = True

    # Download the data
    def _download_data(self):
        if self.all_time:
            self.start_date, self.end_date = None, None

        coin_data = self.download_coin_data(self.coin, self.start_date, self.end_date, self.convert)

        jp = parser.Parser(coin_data)
        self.rows = jp.parse_historical_data()

        self.end_date = self.rows[0][0]
        self.start_date = self.rows[-1][0]

        if self.order_ascending:
            self.rows.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))

        db = database.Storage()
        h_data = db.save_historical_data(self.rows)
        return h_data

    # Download HTML price history for the specified cryptocurrency and time range from CoinMarketCap.
    def download_coin_data(self, coin, start_date, end_date, convert):
        # Setup parameters
        if start_date is None:
            start_date = utils.DEFAULT_START

        if end_date is None:
            end_date = utils.DEFAULT_END

        # Retrieve coin id from name
        db = database.Storage()
        coin_id = db.get_coin_id(coin)
        if coin_id is None:
            return None

        # Convert the date for the URL
        start_date_timestamp = int(round(start_date.timestamp()))
        end_date_timestamp = int(round(end_date.timestamp()))

        # Build URL
        url = self.scraping_url + "/v1/cryptocurrency/ohlcv/historical?convert={}&slug={}&time_end={}&time_start={}"\
                .format(convert, coin_id, end_date_timestamp, start_date_timestamp)

        try:
            json_data = utils.get_url_data(url).json()
            if json_data["status"]["error_code"] != 0:
                raise Exception(json_data["status"]["error_message"])
            return json_data
        except Exception as e:
            print(
                "Error fetching price data for {} for interval '{}' and '{}'",
                coin,
                start_date,
                end_date,
            )

            if hasattr(e, "message"):
                print("Error message (download_data) :", e.message)
            else:
                print("Error message (download_data) :", e)
