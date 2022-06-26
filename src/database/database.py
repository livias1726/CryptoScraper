from sqlite3 import Error
import sqlite3
from time import strptime

from src.database import db_config, db_resources


def _fetch_all(cur, query):
    try:
        cur.execute(query)
        coins = cur.fetchall()
    except sqlite3.OperationalError:
        return None

    return coins


def _fetch_one(cur, query):
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


class DBConnector:
    def __init__(self):
        try:
            self.conn = sqlite3.connect(db_config.NAME)
        except Error:
            print(Error.args)

    # debug
    def delete_table(self, name):
        cur = self.conn.cursor()
        cur.execute("DROP TABLE '%s'" % name)


class DBGetter(DBConnector):

    def get_coins(self):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = ['*']
        query = db_resources.select_from_table(params, 'all_coins', None, None, 'id')
        res = _fetch_all(cur, query)

        # Return
        cur.close()
        return res

    def get_coin_id(self, name):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = ['id']
        cond = {'name': name.capitalize()}
        query = db_resources.select_from_table(params, 'all_coins', None, cond, None)
        c_id = _fetch_one(cur, query)

        # Return
        cur.close()
        return c_id

    def get_categories(self):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = ['name', 'num_tokens', 'market_cap', 'volume']
        query = db_resources.select_from_table(params, 'all_categories', None, None, 'name')
        res = _fetch_all(cur, query)

        # Return
        cur.close()
        return res

    def get_category_id(self, name):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = ['id']
        cond = {'name': name}
        query = db_resources.select_from_table(params, 'all_categories', None, cond, None)
        cat_id = _fetch_one(cur, query)

        # Return
        cur.close()
        return cat_id

    def get_category_coins(self, cat_id):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = ['coin_id', 'name']
        joins = {'table': 'all_coins',
                 'attribute': ['category_coins.coin_id', 'all_coins.id']}
        cond = {'cat_id': cat_id}
        query = db_resources.select_from_table(params, 'category_coins', joins, cond, 'coin_id')
        res = _fetch_all(cur, query)

        # Return
        cur.close()
        return res

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
            price_list = _fetch_all(cur, query)
        else:
            price_list = []
            for c_id in id_list:
                cond = {'id': str(c_id), 'convert': convert}
                query = db_resources.select_from_table(params, 'latest_data', joins, cond, None)
                data = _fetch_all(cur, query)
                if (data is None) or (not data):
                    price_list = None
                    break
                price_list.append(data[0])

        cur.close()
        return price_list

    def get_historical_data(self, coin_id, convert, start, end, descending):
        # Connect
        cur = self.conn.cursor()

        # Select
        params = ['name', 'date', 'convert', 'opening', 'highest', 'lowest', 'closing', 'volume', 'market_cap']
        joins = {'table': 'all_coins',
                 'attribute': 'id'}

        if descending:
            orderby = 'historical_data.date DESC'
        else:
            orderby = 'historical_data.date ASC'

        cond = {'convert': convert, 'date>': str(start).split(' ')[0], 'date<': str(end).split(' ')[0],
                'id': str(coin_id)}

        query = db_resources.select_from_table(params, 'historical_data', joins, cond, orderby)
        data = _fetch_all(cur, query)
        if (data is None) or (not data):
            data = None

        cur.close()
        return data


class DBSetter(DBConnector):

    def __init__(self, data):
        super().__init__()
        self.data = data

    def save_coins(self):
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
            for item in self.data:
                query = db_resources.insert_into_table('all_coins', len(item))
                cur.execute(query, (item['id'], item['name'], item['symbol']))
        else:
            # Update rows
            for item in self.data:
                cond = {'id': item['id']}
                query = db_resources.update_table('all_coins', cond, item)
                print(query)
                cur.execute(query)

        self.conn.commit()
        cur.close()
        self.conn.close()

        return DBGetter().get_coins()

    def save_categories(self):
        # Connect
        cur = self.conn.cursor()

        # Manage table
        query = db_resources.check_if_table_exists('all_categories')
        cur.execute(query)
        if cur.fetchone()[0] != 1:
            # Create table
            columns = {'id': 'text',
                       'name': 'text',
                       'num_tokens': 'integer',
                       'volume': 'real',
                       'market_cap': 'real'
                       }
            pks = ['id']
            query = db_resources.create_table('all_categories', columns, pks)
            cur.execute(query)

            # Insert rows
            for item in self.data:
                query = db_resources.insert_into_table('all_categories', len(item))
                cur.execute(query, (item['id'], item['name'], item['num_tokens'], item['volume'], item['market_cap']))
        else:
            # Update rows
            for item in self.data:
                cond = {'id': item['id']}
                query = db_resources.update_table('all_categories', cond, item)
                cur.execute(query)

        self.conn.commit()
        cur.close()
        self.conn.close()

        return DBGetter().get_categories()

    def save_category_coins(self):
        # Connect
        cur = self.conn.cursor()

        # Manage table
        query = db_resources.check_if_table_exists('category_coins')
        cur.execute(query)
        if cur.fetchone()[0] != 1:
            # Create table
            columns = {'cat_id': 'text REFERENCES all_categories("id")',
                       'coin_id': 'integer REFERENCES all_coins("id")'}
            query = db_resources.create_table('category_coins', columns, None)
            cur.execute(query)

        # Insert rows
        for item in self.data:
            query = db_resources.insert_into_table('category_coins', len(item))
            cur.execute(query, (item['cat_id'], item['coin_id']))

        self.conn.commit()
        cur.close()
        self.conn.close()

        return DBGetter().get_category_coins(self.data[0]['cat_id'])

    def save_latest_data(self, id_list, convert):
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
            pks = ['id', 'convert']
            query = db_resources.create_table('latest_data', columns, pks)
            cur.execute(query)

            # Insert rows
            for item in self.data:
                query = db_resources.insert_into_table('latest_data', len(item))
                cur.execute(query, (item['id'], item['convert'], item['price'], item['volume_24h'],
                                    item['volume_change_24h'], item['percent_change_24h'], item['market_cap'],
                                    item['last_update']))
        else:
            params = ['count(*)']
            for item in self.data:
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

        self.conn.commit()
        cur.close()
        self.conn.close()

        return DBGetter().get_latest_data(id_list, convert)

    def save_historical_data(self, coin_id, convert, start, end, descending, first_data):
        is_new = False

        # Connect
        cur = self.conn.cursor()

        # Manage table
        query = db_resources.check_if_table_exists("historical_data")
        cur.execute(query)
        if cur.fetchone()[0] != 1:  # Table does not exist
            # Create table
            columns = {'id': 'integer REFERENCES all_coins("id")',
                       'date': 'text',
                       'convert': 'text',
                       'opening': 'real',
                       'highest': 'real',
                       'lowest': 'real',
                       'closing': 'real',
                       'volume': 'integer',
                       'market_cap': 'real',
                       'first_data': 'bool'}
            pks = ['id', 'date', 'convert']
            query = db_resources.create_table('historical_data', columns, pks)
            cur.execute(query)
            is_new = True

        if not is_new:
            self._filter_insert(coin_id, convert, start, end, descending)

            if len(self.data) == 0:
                return DBGetter().get_historical_data(coin_id, convert, start, end, descending)

        # Insert rows
        for item in self.data:
            query = db_resources.insert_into_table('historical_data', len(item) + 1)
            # The data are the oldest on CoinMarketCap for that coin and the first record for that coin
            if first_data and (item == self.data[0]):
                cur.execute(query, (item['id'], item['date'], item['convert'], item['open'], item['high'], item['low'],
                                    item['close'], item['volume'], item['market_cap'], True))
                continue

            # Else
            cur.execute(query, (item['id'], item['date'], item['convert'], item['open'], item['high'], item['low'],
                                item['close'], item['volume'], item['market_cap'], False))

        self.conn.commit()
        cur.close()
        self.conn.close()

        return DBGetter().get_historical_data(coin_id, convert, start, end, descending)

    # Retrieve the missing data to store
    def _filter_insert(self, coin_id, convert, start, end, descending):
        # Get stored data
        stored_data = DBGetter().get_historical_data(coin_id, convert, start, end, descending)

        if stored_data is None:  # If no historical data for this coin is stored: insert all data
            return

        tot = len(self.data)
        filtered = []

        j = 0
        while j < tot:
            for i in range(0, len(stored_data)):
                while strptime(self.data[j]['date'], '%Y-%m-%d') != strptime(stored_data[i][1], '%Y-%m-%d'):
                    filtered.append(self.data[j])
                    j = j + 1
                j = j + 1

        self.data = filtered
