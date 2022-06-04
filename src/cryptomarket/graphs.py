from datetime import datetime

from src.cryptomarket import utils, data, parser
import matplotlib.pyplot as plt


class Graph:
    """
    Graph: the class to show the requested plots
    """
    # The constructor takes:
    #   - the main coin to get plots for
    #   - the main observable to plot for that coin
    #   - the offset of temporal data to plot
    #   - the time interval of the data to retrieve
    #   - the fiat currency
    def __init__(self, coin, observable, offset=utils.DEFAULT_OFFSET, start=utils.DEFAULT_START, end=utils.DEFAULT_END,
                 convert=utils.DEFAULT_CONVERT):

        self.coin = coin
        self.observable = observable

        self.offset = offset
        self.start = start
        self.end = end

        self.convert = convert

        # Attributes to compute for plotting
        self._set_obs_idx(observable)

    def _fetch_data(self, coin):
        cmc = data.CMCHistorical(self.start, self.end, False, self.convert)
        dataset = cmc.get_historical_data(coin)

        return dataset

    def _get_axes(self, coin=None, observable=None):
        if coin is None:
            coin = self.coin

        if observable is None:
            observable = self.observable
        else:
            self._set_obs_idx(observable)

        # Get dataset
        dataset = self._fetch_data(coin)

        # Parse data for the wanted observable
        j = parser.ObservablesParser(dataset, observable, self.num_observable)
        items = j.get_observables()

        # Prepare axes
        dates = [j["date"] for j in items]
        obs = [j[observable] for j in items]

        return dates, obs
                
    def show_observable(self):
        x, y = self._get_axes()

        if self.offset != utils.DEFAULT_OFFSET:
            # Parse data
            tr = parser.Trimmer(self.offset, x, y)
            x, y = tr.trim_data()

            if x is None:
                return

        # Design
        des = _Designer(self.coin, self.observable, self.offset, self.convert, self._get_obs_title(self.observable))
        des.design_single_line_plot(x, y)

    def show_obs_pairing(self, observables):
        dates, first_data = self._get_axes()
        if self.offset != utils.DEFAULT_OFFSET:
            # Parse data
            tr = parser.Trimmer(self.offset, dates, first_data)
            dates, first_data = tr.trim_data()

            if dates is None:
                return

        header = [self.observable.capitalize()]
        data_array = [first_data]

        for obs in observables:
            x, y = self._get_axes(observable=obs)

            if self.offset != utils.DEFAULT_OFFSET:
                # Parse data
                tr = parser.Trimmer(self.offset, x, y)
                x, y = tr.trim_data()

                if x is None:
                    return

            header.append(obs.capitalize())
            data_array.append(y)

        # Design
        title = self.coin.capitalize() + ' observables pairing'
        des = _Designer(self.coin, self.observable, self.offset, self.convert)
        des.design_multi_lines_plot(title, header, data_array, dates)

    def show_coins_pairing(self, coins):
        # Get data for the main coin (the one passed to the constructor of the class)
        dates, first_data = self._get_axes()

        header = [self.coin.capitalize()]
        dates_array = [dates]
        data_array = [first_data]

        # Get data for every other coin requested in input
        for coin in coins:
            x, y = self._get_axes(coin)
            x_date = datetime.strptime(x[0], '%Y-%m-%d')

            if x_date > self.start:
                self.start = x_date  # Update start date for other coins
                # Process the stored data to align the starting date
                dates_array, data_array = self._process_coin_data(dates_array, data_array, True)

            elif x_date < self.start:
                # Process the retrieved data to align the starting date
                x, y = self._process_coin_data(x, y, False)

            header.append(coin.capitalize())
            dates_array.append(x)
            data_array.append(y)

        if self.offset != utils.DEFAULT_OFFSET:
            for idx in range(len(dates_array)):
                # Parse data
                x = dates_array[idx]
                y = data_array[idx]

                tr = parser.Trimmer(self.offset, x, y)
                dates_array[idx], data_array[idx] = tr.trim_data()

                if dates_array[idx] is None:
                    return

        dates = dates_array[0]

        # Design
        title = self.observable.capitalize() + ' price for coins pairing'
        des = _Designer(self.coin, self.observable, self.offset, self.convert)
        des.design_multi_lines_plot(title, header, data_array, dates)

    """
    The moving average is compute in terms of number of days.
    If on_data is true, the MA is shown against the data on which it is computed.
    """
    def show_moving_average(self, n, on_data):
        # Get data
        dates, data = self._get_axes()
        dates_array = [dates]

        # Check if MA is computable
        if len(data) < n:
            print("Too few data. Try to extend the period of observation or reduce the MA index")
            return None

        # Compute the first n days
        moving_averages = utils.get_moving_average(data, n)
        data_array = [moving_averages]

        title = self.coin.capitalize() + " " + self.observable + ' SMA on ' + str(n) + " days"

        # Prepare axes
        if on_data:
            data_array.append(data[n-1:])
            header = ["MA(" + str(n) + ")", self.observable.capitalize()]

            # Design
            des = _Designer(self.coin, self.observable, self.offset, self.convert)
            des.design_multi_lines_plot(title, header, data_array, dates[n-1:])
        else:
            # Design
            des = _Designer(self.coin, self.observable, self.offset, self.convert)
            des.design_single_line_plot(dates[n-1:], moving_averages, title)

    def show_latest_pairing(self):
        pass

    def _set_obs_idx(self, observable):
        if observable == 'open':
            self.num_observable = 3
        elif observable == 'high':
            self.num_observable = 4
        elif observable == 'low':
            self.num_observable = 5
        elif self.observable == 'close':
            self.num_observable = 6
        elif self.observable == 'volume':
            self.num_observable = 7
        elif self.observable == 'market_cap':
            self.num_observable = 8

    def _get_obs_title(self, observable):
        if observable == 'open':
            return "opening prices"
        elif observable == 'high':
            return "higher prices"
        elif observable == 'low':
            return "lower prices"
        elif self.observable == 'close':
            return "closing prices"
        elif self.observable == 'volume':
            return "volume"
        elif self.observable == 'market_cap':
            return "market cap."

    def _process_coin_data(self, dates, prices, is_list):

        if is_list:
            for idx_ext in range(len(dates)):  # For every coin already retrieved
                for idx_int in range(len(dates[idx_ext])):    # Get the amount of data to remove
                    date = datetime.strptime(dates[idx_ext][idx_int], '%Y-%m-%d')
                    if date == self.start:
                        # Remove data
                        dates[idx_ext] = dates[idx_ext][idx_int:]
                        prices[idx_ext] = prices[idx_ext][idx_int:]

                        break
        else:
            for idx in range(len(dates)):  # Get the amount of data to remove
                if datetime.strptime(dates[idx], '%Y-%m-%d') == self.start:
                    # Remove data
                    dates = dates[idx:]
                    prices = prices[idx:]

                    break

        return dates, prices


class _Designer(Graph):

    def __init__(self, coin, observable, offset, convert, obs_title=None, style=utils.DEFAULT_STYLE):
        super().__init__(coin, observable)

        self.obs_title = obs_title
        self._set_offset_title(offset)
        self.convert = convert
        self.style = style

    def _set_offset_title(self, offset):
        if offset == 'w':
            self.offset_title = "weekly"
        elif offset == 'm':
            self.offset_title = "monthly"
        elif offset == 'y':
            self.offset_title = "yearly"
        else:
            self.offset_title = "daily"

    def design_single_line_plot(self, x, y, title=None):
        plt.style.use(self.style)
        plt.figure(figsize=utils.set_size(32, 18))

        plt.plot(x, y)
        if title is None:
            plt.title(self.coin.capitalize() + ' ' + self.obs_title + ' ' + self.offset_title)
        else:
            plt.title(title)

        plt.xlabel('Date')
        plt.ylabel('Price in %s' % self.convert)
        plt.xticks(rotation=45)

        plt.show()

    def design_bar_plot(self):
        pass

    def design_multi_lines_plot(self, title, header, data_array, dates):
        plt.style.use(self.style)
        plt.figure(figsize=utils.set_size(32, 18))

        plt.plot()
        for y in data_array:
            plt.plot(dates, y)

        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Price in %s' % self.convert)
        plt.legend(header, loc='upper left')

        plt.xticks(rotation=45)

        plt.show()
