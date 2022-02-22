from src.cryptomarket.CMC import CMC
import src.database.database as database
import src.cryptomarket.jsonparser as jp


# https://coinmarketcap.com/api/documentation/v1/


class CMCListing(CMC):

    def get_coins(self):
        # Retrieve data from db
        db = database.DB()
        data_list = db.get_coins()
        if data_list is not None:
            return data_list

        # Update data on db
        res = self.update_coin_listing()
        return res

    # Credit: 1 per call
    def get_categories(self):
        # Retrieve data from db
        db = database.DB()
        data_list = db.get_categories()
        if data_list is not None:
            return data_list

        # Update data on db
        data_list = self.update_category_listing()
        return data_list

    # Credit: 1 per call + 1 per 200 curr
    def get_coins_for_category(self, name):
        # Retrieve data from db
        db = database.DB()
        cat_id = db.get_category_id(name)
        if cat_id is None:
            return "Category not found. Try to update the database by calling 'update_category_listing()'"

        data_list = db.get_category_coins(cat_id)
        if data_list is not None:
            return data_list

        # Update data on db
        data_list = self.update_coins_per_category(name)
        return data_list

    # Credit: 1 per call
    def update_coin_listing(self):
        # Get data from API
        url = self.apiUrl + '/v1/cryptocurrency/map'
        r = self.session.get(url)
        data = r.json()

        # Parse json response
        data_list = jp.parse_all_coins(data)

        # Save data on db
        db = database.DB()
        data_list = db.save_coins(data_list)

        return data_list

    def update_category_listing(self):
        # Get data from API
        url = self.apiUrl + '/v1/cryptocurrency/categories'
        r = self.session.get(url)
        data = r.json()

        # Parse json response
        data_list = jp.parse_all_categories(data)

        # Save data on db
        db = database.DB()
        data_list = db.save_categories(data_list)

        return data_list

    def update_coins_per_category(self, name):
        # Retrieve data from db
        db = database.DB()
        cat_id = db.get_category_id(name)
        if cat_id is None:
            return "Category not found. Try to update the database by calling 'update_category_listing()'"

        # Get data from API
        url = self.apiUrl + '/v1/cryptocurrency/category'
        parameters = {'id': cat_id}
        r = self.session.get(url, params=parameters)
        data = r.json()

        # Parse json response
        data_list = jp.parse_category_coins(data, cat_id, name)

        # save data in db
        db = database.DB()
        data_list = db.save_category_coins(data_list)
        return data_list
