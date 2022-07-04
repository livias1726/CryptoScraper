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


class Trimmer:

    def __init__(self, time_offset, time_data, obs_data):
        self.time_offset = time_offset
        self.time_data = time_data
        self.obs_data = obs_data

    def trim_data(self):
        if self.time_offset == 'w':
            return self._trim_weekly()
        elif self.time_offset == 'm':
            return self._trim_monthly()
        elif self.time_offset == 'y':
            return self._trim_yearly()
        else:
            print("Invalid time offset.")
            return None, None

    def _trim_yearly(self):
        base = self.time_data[0]
        x = [base]
        y = [self.obs_data[0]]

        date = datetime.strptime(base, "%Y-%m-%d")

        day = date.day
        month = date.month
        year = date.year

        for i in range(1, len(self.time_data)):
            day_i = datetime.strptime(self.time_data[i], "%Y-%m-%d").day
            month_i = datetime.strptime(self.time_data[i], "%Y-%m-%d").month
            year_i = datetime.strptime(self.time_data[i], "%Y-%m-%d").year

            if (day_i == day) and (month_i == month) and (year_i != year):
                x.append(self.time_data[i])
                y.append(self.obs_data[i])
                year = datetime.strptime(self.time_data[i], "%Y-%m-%d").year

        return x, y

    def _trim_monthly(self):
        base = self.time_data[0]
        x = [base]
        y = [self.obs_data[0]]

        day = datetime.strptime(base, "%Y-%m-%d").day
        for i in range(1, len(self.time_data)):
            if datetime.strptime(self.time_data[i], "%Y-%m-%d").day is day:
                x.append(self.time_data[i])
                y.append(self.obs_data[i])

        return x, y

    def _trim_weekly(self):
        base = self.time_data[0]
        x = [base]
        y = [self.obs_data[0]]

        for i in range(6, len(self.time_data), 7):
            x.append(self.time_data[i])
            y.append(self.obs_data[i])

        return x, y
