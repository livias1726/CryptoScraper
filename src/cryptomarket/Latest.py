from src.cryptomarket import utils, Listing
from src.cryptomarket.CMC import CMC
import src.database.database as database
import src.cryptomarket.jsonparser as jp


# https://coinmarketcap.com/api/documentation/v1/


class CMCLatest(CMC):

    def get_latest_data(self, names, convert):
        # Retrieve data from db
        db = database.DB()
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
        db = database.DB()

        listing = Listing.CMCListing()
        data_list = listing.get_coins_for_category(cat_name)

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
        db = database.DB()
        if id_list is None:
            url = self.apiUrl + '/v1/cryptocurrency/listings/latest'
            parameters = {'start': '1',
                          'limit': '200',
                          'convert': convert}
            r = self.session.get(url, params=parameters)
            data = r.json()
        else:
            url = self.apiUrl + '/v1/cryptocurrency/quotes/latest'

            id_str = ""
            for i in range(len(id_list) - 1):
                id_str = id_str + str(id_list[i]) + ","
            id_str = id_str + str(id_list[len(id_list) - 1])
            parameters = {'id': id_str,
                          'convert': convert}

            r = self.session.get(url, params=parameters)
            data = r.json()

        # Parse json response
        data_list = jp.parse_latest_data(data, id_list, convert)

        # Save data in db
        data_list = db.save_latest_data(data_list, id_list, convert)

        return data_list
