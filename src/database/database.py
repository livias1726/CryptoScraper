from sqlite3 import Error
import sqlite3

from src.database import db_config, db_resources


class DB:
    def __init__(self):
        try:
            self.conn = sqlite3.connect(db_config.NAME)
        except Error:
            print(Error.args)

    def __fetch_all(self, cur, query):
        try:
            cur.execute(query)
            coins = cur.fetchall()
        except sqlite3.OperationalError:
            return None

        return coins

    def __fetch_one(self, cur, query):
        try:
            cur.execute(query)
            c_id = cur.fetchone()
            if c_id is None:
                res = None
            else:
                res = c_id[0]
        except sqlite3.OperationalError:
            res = None

        return res

    def get_coins(self):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = ['*']
        query = db_resources.select_from_table(params, 'all_coins', None, None, 'id')
        return self.__fetch_all(cur, query)

    def save_coins(self, data_list):
        # Connect
        cur = self.conn.cursor()

        # Manage table
        query = db_resources.check_if_table_exists('all_coins')
        cur.execute(query)
        if cur.fetchone()[0] != 1:
            # Create table
            columns = {
                'id': 'integer',
                'name': 'text',
                'symbol': 'text',
            }
            pks = ['id']
            query = db_resources.create_table('all_coins', columns, pks)
            cur.execute(query)

            # Insert rows
            for item in data_list:
                query = db_resources.insert_into_table('all_coins', len(item))
                cur.execute(query, (item['id'], item['name'], item['symbol']))
        else:
            # Update rows
            for item in data_list:
                cond = {'id': item['id']}
                query = db_resources.update_table('all_coins', cond, item)
                cur.execute(query)

        self.conn.commit()
        cur.close()
        return self.get_coins()

    def get_coin_id(self, name):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = ['id']
        cond = {'name': name.capitalize()}
        query = db_resources.select_from_table(params, 'all_coins', None, cond, None)
        return self.__fetch_one(cur, query)

    def get_categories(self):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = {'name', 'num_tokens', 'market_cap', 'volume'}
        query = db_resources.select_from_table(params, 'all_categories', None, None, 'name')
        return self.__fetch_all(cur, query)

    def save_categories(self, data_list):
        # Connect
        cur = self.conn.cursor()

        # Manage table
        cur.execute(db_resources.check_if_table_exists('all_categories'))
        if cur.fetchone()[0] != 1:
            # Create table
            columns = {
                'id': 'integer',
                'name': 'text',
                'num_tokens': 'integer',
                'market_cap': 'real',
                'volume': 'real'
            }
            pks = ['id']
            query = db_resources.create_table('all_categories', columns, pks)
            cur.execute(query)

            # Insert rows
            for item in data_list:
                query = db_resources.insert_into_table('all_categories', len(item))
                cur.execute(query, (item['id'], item['name'], item['num_tokens'], item['market_cap'], item['volume']))
        else:
            # Update rows
            for item in data_list:
                cond = {'id': item['id']}
                query = db_resources.update_table('all_categories', cond, item)
                cur.execute(query)

        # Return
        self.conn.commit()
        cur.close()
        return self.get_categories()

    def get_category_id(self, name):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = {'id'}
        cond = {'name': name}
        query = db_resources.select_from_table(params, 'all_categories', None, cond, None)
        return self.__fetch_one(cur, query)

    def get_category_coins(self, cat_id):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = {'coin_id', 'coin_name'}
        cond = {'cat_id': cat_id}
        query = db_resources.select_from_table(params, 'category_coins', None, cond, None)
        return self.__fetch_all(cur, query)

    def save_category_coins(self, data_list):
        # Connect
        cur = self.conn.cursor()

        # Manage table
        query = db_resources.check_if_table_exists('category_coins')
        cur.execute(query)
        if cur.fetchone()[0] != 1:
            # Create table
            columns = {
                'cat_id': 'text REFERENCES all_categories("id")',
                'coin_id': 'integer REFERENCES all_coins("id")'
            }
            query = db_resources.create_table('category_coins', columns, None)
            cur.execute(query)

            # Insert rows
            for item in data_list:
                query = db_resources.insert_into_table('category_coins', len(item))
                cur.execute(query, (item['cat_id'], item['coin_id']))
        else:
            # Update rows
            for item in data_list:
                cond = {'id': item['id']}
                query = db_resources.update_table('category_coins', cond, item)
                cur.execute(query)

        # Return
        self.conn.commit()
        cur.close()
        return self.get_category_coins(data_list[0]['cat_id'])

    def get_latest_data(self, id_list, convert):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = ['name', 'convert', 'price', 'volume_24h', 'volume_change_24h', 'percent_change_24h', 'market_cap',
                  'last_update']
        joins = {'table': 'all_coins',
                 'attribute': 'id'}

        if id_list is None:
            cond = {'convert': convert}
            query = db_resources.select_from_table(params, 'latest_data', joins, cond, None)
            price_list = self.__fetch_all(cur, query)
        else:
            price_list = []
            for c_id in id_list:
                cond = {'id': str(c_id), 'convert': convert}
                query = db_resources.select_from_table(params, 'latest_data', joins, cond, None)
                data = self.__fetch_all(cur, query)
                if (data is None) or (not data):
                    price_list = None
                    break
                price_list.append(data)

        cur.close()
        return price_list

    def save_latest_data(self, data_list, id_list, convert):
        # Connect
        cur = self.conn.cursor()
        # Manage table
        query = db_resources.check_if_table_exists('latest_data')
        cur.execute(query)

        if cur.fetchone()[0] != 1:
            # Create table
            columns = {
                'id': 'integer REFERENCES all_coins("id")',
                'convert': 'text',
                'price': 'real',
                'volume_24h': 'integer',
                'volume_change_24h': 'real',
                'percent_change_24h': 'real',
                'market_cap': 'real',
                'last_update': 'text'
            }
            query = db_resources.create_table('latest_data', columns, None)
            cur.execute(query)

            # Insert rows
            for item in data_list:
                query = db_resources.insert_into_table('latest_data', len(item))
                cur.execute(query, (item['id'], item['convert'], item['price'], item['volume_24h'],
                                    item['volume_change_24h'], item['percent_change_24h'], item['market_cap'],
                                    item['last_update']))
        else:
            params = ['count(*)']
            for item in data_list:
                # Check existence
                cond = {'id': str(item['id']),
                        'convert': convert}
                query = db_resources.select_from_table(params, 'latest_data', None, cond, None)
                cur.execute(query)
                if cur.fetchone()[0] != 0:
                    # Update
                    query = db_resources.update_table('latest_data', cond, item)
                    cur.execute(query)
                else:
                    # Insert
                    query = db_resources.insert_into_table('latest_data', len(item))
                    cur.execute(query, (item['id'], item['convert'], item['price'], item['volume_24h'],
                                        item['volume_change_24h'], item['percent_change_24h'], item['market_cap'],
                                        item['last_update']))

        # Return
        self.conn.commit()
        cur.close()
        return self.get_latest_data(id_list, convert)

    # debug
    def delete_table(self, name):
        cur = self.conn.cursor()
        cur.execute("DROP TABLE '%s'" % name)
