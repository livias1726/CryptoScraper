from src.cryptomarket import utils, data, parser
import matplotlib.pyplot as plt

"""
DOC
"""


class Graph:
    def __init__(self, coin, observable, offset=utils.DEFAULT_OFFSET, start=utils.DEFAULT_START, end=utils.DEFAULT_END,
                 convert=utils.DEFAULT_CONVERT):

        self.coin = coin
        self.observable = observable
        self._set_obs_idx()

        self.offset = offset
        self.start = start
        self.end = end

        self.convert = convert

    def _get_axes(self):
        # Get dataset
        dataset = self._fetch_data(self.start, self.end, self.convert)

        # Parse data for the wanted observable
        i = parser.ObservablesParser(dataset, self.observable, self.num_observable)
        items = i.get_observables()

        # Prepare axes
        x = [i["date"] for i in items]
        y = [i[self.observable] for i in items]

        return x, y

    def show_observable(self):
        x, y = self._get_axes()

        if self.offset != utils.DEFAULT_OFFSET:
            # Parse data
            tr = parser.Trimmer(self.offset, x, y)
            x, y = tr.trim_data()

            if x is None:
                return

        # Design
        des = _Designer(self.coin, self.observable, self.observable_title, self.offset, self.convert)
        des.design_single_line_plot(x, y)

    def show_obs_pairing(self):
        pass

    def show_coins_pairing(self, coins):
        data_array = {}

        for idx in range(len(coins)):
            x, y = self._get_axes()

            if self.offset != utils.DEFAULT_OFFSET:
                # Parse data
                tr = parser.Trimmer(self.offset, x, y)
                x, y = tr.trim_data()

                if x is None:
                    return

            data_array[idx] = x

        # Design
        des = _Designer(self.coin, self.observable, self.observable_title, self.offset, self.convert)
        des.design_multi_lines_plot(data_array, y)

    # if on_data flag is true, the MA is shown on the observable
    def show_moving_average(self, n, on_data):
        global i
        local_start = None

        # Manage time intervals
        if self.start != utils.DEFAULT_START:
            local_start = self.start
            self.start = utils.DEFAULT_START
        x, y = self._get_axes()

        # Check if MA is computable
        if len(x) < n:
            print("Too few data. Try to extend the period of observation or reduce the MA index")
            return None

        # Restore requested time interval
        if local_start is not None:
            self.start = local_start

        # Compute the first n days
        # TODO: compute ma considering start value different than default

        ma_sum = 0
        ma = []
        for i in range(n):
            ma_sum += y[i]
        ma.append(ma_sum / n)

        # Compute the whole MA
        while i < len(x):
            ma_sum = ma_sum + y[i] - y[i - n]
            ma.append(ma_sum / n)
            i += 1

        # Prepare axes
        if on_data:
            if self.offset != utils.DEFAULT_OFFSET:
                # Parse data
                tr = parser.Trimmer(self.offset, x, y)
                x, y = tr.trim_data()
                if x is None:
                    return

                tr = parser.Trimmer(self.offset, x, ma)
                x, ma = tr.trim_data()

                if x is None:
                    return

            y = y[n:len(x)]
        x = x[n:len(x)]

        # Design
        des = _Designer(self.coin, self.observable, self.observable_title, self.offset, self.convert)
        des.design_pair_line_plot(x, y, ma)

    def show_latest_pairing(self):
        pass

    def _fetch_data(self, start, end, convert):
        cmc = data.CMCHistorical(self.coin, start, end, False, convert)
        dataset = cmc.get_historical_data()

        # Discard header
        dataset = dataset[1:]

        return dataset

    def _set_obs_idx(self):
        if self.observable == 'open':
            self.num_observable = 3
            self.observable_title = "opening prices"
        elif self.observable == 'high':
            self.num_observable = 4
            self.observable_title = "higher prices"
        elif self.observable == 'low':
            self.num_observable = 5
            self.observable_title = "lower prices"
        elif self.observable == 'close':
            self.observable_title = "closing prices"
            self.num_observable = 6
        elif self.observable == 'volume':
            self.num_observable = 7
            self.observable_title = "volume"
        elif self.observable == 'market_cap':
            self.num_observable = 8
            self.observable_title = "market cap."


"""
DOC
"""


class _Designer(Graph):

    def __init__(self, coin, observable, obs_title, offset, convert):
        super().__init__(coin, observable)

        self.obs_title = obs_title
        self._set_offset_title(offset)
        self.convert = convert

    def _set_offset_title(self, offset):
        if offset == 'w':
            self.offset_title = "weekly"
        elif offset == 'm':
            self.offset_title = "monthly"
        elif offset == 'y':
            self.offset_title = "yearly"
        else:
            self.offset_title = "daily"

    def design_single_line_plot(self, x, y):
        plt.plot(x, y)

        plt.title(self.coin.capitalize() + ' ' + self.obs_title + ' ' + self.offset_title)
        plt.xlabel('Date')
        plt.ylabel('Price in %s' % self.convert)

        plt.xticks(rotation=45)

        plt.show()

    def design_pair_line_plot(self, x, y, z):
        plt.plot(x, y)
        plt.plot(x, z)

        plt.title(self.coin.capitalize() + ' ' + self.obs_title + ' ' + self.offset_title)
        plt.xlabel('Date')
        plt.ylabel('Price in %s' % self.convert)

        plt.xticks(rotation=45)

        plt.show()

    def design_bar_plot(self):
        pass
