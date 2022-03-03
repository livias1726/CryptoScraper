from _datetime import datetime


class JsonParser:
    def __init__(self, json_data):
        self.json_data = json_data

    def _parse_data(self):
        item_list = self.json_data
        while 'data' in item_list:
            item_list = item_list['data']
        return item_list

    # Gets coin generalities from 'cryptocurrency/map' call
    def parse_all_coins(self):
        item_list = self._parse_data()
        res = []
        for item in item_list:
            i = {'id': item['id'], 'name': item['name'], 'symbol': item['symbol']}
            res.append(i)
        return res

    # Gets category generalities from 'cryptocurrency/categories' call
    def parse_all_categories(self):
        item_list = self._parse_data()
        res = []
        for item in item_list:
            i = {'id': item['id'],
                 'name': item['name'],
                 'num_tokens': item['num_tokens'],
                 'market_cap': item['market_cap'],
                 'volume': item['volume']}
            res.append(i)
        return res

    # Gets all coins from a category with 'cryptocurrency/category' call
    def parse_category_coins(self, cat_id):
        item_list = self._parse_data()
        item_list = item_list['coins']
        res = []
        for item in item_list:
            i = {'coin_id': item['id'],
                 'cat_id': cat_id}
            res.append(i)
        return res

    # Get cryptocurrencies current data on price, volume, volume change in 24h,
    # price percentage change in 24h, market capital
    def parse_latest_data(self, id_list, convert):
        item_list = self._parse_data()
        res = []
        if id_list is not None:
            for c_id in id_list:
                data = item_list[str(c_id)]['quote'][convert]
                res.append({'id': c_id,
                            'convert': convert,
                            'price': data['price'],
                            'volume_24h': data['volume_24h'],
                            'volume_change_24h': data['volume_change_24h'],
                            'percent_change_24h': data['percent_change_24h'],
                            'market_cap': data['market_cap'],
                            'last_update': data['last_updated']})
        else:
            if type(item_list) is not list:
                item_list = [item_list]
            for item in item_list:
                data = item['quote'][convert]
                i = {'id': item['id'],
                     'convert': convert,
                     'price': data['price'],
                     'volume_24h': data['volume_24h'],
                     'volume_change_24h': data['volume_change_24h'],
                     'percent_change_24h': data['percent_change_24h'],
                     'market_cap': data['market_cap'],
                     'last_update': data['last_updated']}
                res.append(i)
        return res

    def parse_historical_data(self, convert):
        item_list = self._parse_data()

        if type(item_list) is not list:
            item_list = [item_list]

        rows = []
        for coin in item_list:
            c_id = coin["id"]
            for data in coin["quotes"]:
                quote = list(data["quote"].values())[0]
                date = datetime.strptime(quote["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")

                row = {"id": c_id,
                       "date": date,
                       "convert": convert,
                       "open": quote["open"],
                       "high": quote["high"],
                       "low": quote["low"],
                       "close": quote["close"],
                       "volume": quote["volume"],
                       "market_cap": quote["market_cap"]
                       }

                rows.append(row)

        return rows


class ObservablesParser:
    def __init__(self, dataset, data_name, data_idx):
        self.dataset = dataset
        self.data_name = data_name
        self.data_idx = data_idx

    def get_observables(self):
        obs = []
        for data in self.dataset:
            ob = {'date': data[1], self.data_name: data[self.data_idx]}
            obs.append(ob)
        return obs
