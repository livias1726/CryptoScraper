from datetime import datetime

import matplotlib.dates

from src.cryptomarket import utils, data, parser
import matplotlib.pyplot as plt
import pandas as pd

from src.cryptomarket.data import CMCHistorical


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

        if start != utils.DEFAULT_START:
            self.start = datetime.strptime(start, "%Y-%m-%d")
        else:
            self.start = start

        if end != utils.DEFAULT_END:
            self.end = datetime.strptime(end, "%Y-%m-%d")
        else:
            self.end = end

        self.convert = convert

        # Attributes to compute for plotting
        self._set_obs_idx(observable)

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

    def _fetch_data(self, coin):
        cmc = data.CMCHistorical(self.start, self.end, False, self.convert)
        dataset = cmc.get_historical_data(coin)

        return dataset

    def show_observable(self):
        x, y = self._get_axes()

        # Update data to the requested end date
        if datetime.strptime(x[-1], '%Y-%m-%d').date() < self.end.date():
            cmc = CMCHistorical()
            cmc.update_historical_data(self.coin)
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
        if datetime.strptime(dates[-1], '%Y-%m-%d').date() < self.end.date():  # Update data to the requested end date
            cmc = CMCHistorical()
            cmc.update_historical_data(self.coin)
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
        des = _Designer(self.coin, self.observable, offset=self.offset, convert=self.convert)
        des.design_multi_lines_plot(title, header, data_array, dates)

    def show_coins_pairing(self, coins, correlation=False):
        if correlation and len(coins) != 1:
            print("Invalid arguments: to show a correlation between coins "
                  "enter a single coin to pair with the main one.")
            return

        # Get data for the main coin (the one passed to the constructor of the class)
        dates, first_data = self._get_axes()
        if datetime.strptime(dates[-1], '%Y-%m-%d').date() < self.end.date():  # Update data to the requested end date
            cmc = CMCHistorical()
            cmc.update_historical_data(self.coin)
            dates, first_data = self._get_axes()

        header = [self.coin.capitalize()]
        dates_array = [dates]
        data_array = [first_data]

        # Get data for every other coin requested in input
        for coin in coins:
            x, y = self._get_axes(coin)
            if len(y) < len(data_array[-1]):  # Stored data for the current coin needs to be updated!
                cmc = CMCHistorical()
                cmc.update_historical_data(coin)
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
        des = _Designer(self.coin, self.observable, offset=self.offset, convert=self.convert, correlation=correlation)
        des.design_multi_lines_plot(title, header, data_array, dates)

    """
    The moving average is compute in terms of number of days.
    If on_data is true, the MA is shown against the data on which it is computed.
    """
    def show_sma(self, list_of_days, on_data=True):
        # Get data
        dates, obs_data = self._get_axes()
        if datetime.strptime(dates[-1], '%Y-%m-%d').date() < self.end.date():  # Update data to the requested end date
            cmc = CMCHistorical()
            cmc.update_historical_data(self.coin)
            dates, obs_data = self._get_axes()

        temp = list_of_days[0]
        for days in list_of_days:  # Get the largest value
            if len(obs_data) < days:
                print("Too few data. Try to extend the period of observation or reduce the MA index")
                return None

            if temp < days:
                temp = days

        data_array = []
        header = []
        # Check if MA is computable
        for days in list_of_days:
            # Compute SMA
            smas = utils.compute_sma(obs_data, days)
            data_array.append(smas[temp-days:])
            header.append("SMA(" + str(days) + ")")

        if len(list_of_days) == 1:
            title = self.coin.capitalize() + " " + self.observable + ' SMA on ' + str(list_of_days[0]) + " days"
        else:
            title = self.coin.capitalize() + " " + self.observable + ' SMA'

        # Prepare axes
        if on_data:
            data_array.append(obs_data[temp - 1:])
            header.append(self.observable.capitalize())

        # Design
        des = _Designer(self.coin, self.observable, self.offset, self.convert)
        des.design_multi_lines_plot(title, header, data_array, dates[temp - 1:])

    def show_ema(self, list_of_days, smooth, on_data=True):
        # Get data
        dates, obs_data = self._get_axes()
        if datetime.strptime(dates[-1], '%Y-%m-%d').date() < self.end.date():  # Update data to the requested end date
            cmc = CMCHistorical()
            cmc.update_historical_data(self.coin)
            dates, obs_data = self._get_axes()

        temp = list_of_days[0]
        for days in list_of_days:  # Get the largest value
            if len(obs_data) < days+1:  # Check if EMA is computable
                print("Too few data. Try to extend the period of observation or reduce the MA index")
                return None

            if temp < days:
                temp = days

        data_array = []
        header = []
        for days in list_of_days:
            # Compute EMA
            emas = utils.compute_ema(obs_data, days, smooth)
            data_array.append(emas[temp - days:])
            header.append("EMA(" + str(days) + ")")

        if len(list_of_days) == 1:
            title = self.coin.capitalize() + " " + self.observable + ' EMA on ' + str(list_of_days[0]) + " days"
        else:
            title = self.coin.capitalize() + " " + self.observable + ' EMA'

        # Prepare axes
        if on_data:
            data_array.append(obs_data[temp - 1:])
            header.append(self.observable.capitalize())

        # Design
        des = _Designer(self.coin, self.observable, self.offset, self.convert)
        des.design_multi_lines_plot(title, header, data_array, dates[temp - 1:])

    def show_ma(self, days, smooth, on_data=True):
        # Get data
        dates, obs_data = self._get_axes()
        if datetime.strptime(dates[-1], '%Y-%m-%d').date() < self.end.date():  # Update data to the requested end date
            cmc = CMCHistorical()
            cmc.update_historical_data(self.coin)
            dates, obs_data = self._get_axes()

        if len(obs_data) < days + 1:  # Check if EMA is computable
            print("Too few data. Try to extend the period of observation or reduce the MA index")
            return None

        # Compute SMA
        smas = utils.compute_sma(obs_data, days)
        data_array = [smas]
        header = ["SMA(" + str(days) + ")"]

        # Compute EMA
        emas = utils.compute_ema(obs_data, days, smooth)
        data_array.append(emas)
        header.append("EMA(" + str(days) + ")")

        title = self.coin.capitalize() + " " + self.observable + ' moving averages on ' + str(days) + " days"

        # Prepare axes
        if on_data:
            data_array.append(obs_data[days - 1:])
            header.append(self.observable.capitalize())

        # Design
        des = _Designer(self.coin, self.observable, self.offset, self.convert)
        des.design_multi_lines_plot(title, header, data_array, dates[days - 1:])

    def show_latest_pairing(self):
        pass

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

    def __init__(self, coin, observable, offset, convert, obs_title=None, correlation=False, style=utils.DEFAULT_STYLE):
        super().__init__(coin, observable)

        self.obs_title = obs_title
        self._set_offset_title(offset)
        self.convert = convert
        self.correlation = correlation
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
        fig, ax = plt.subplots(figsize=utils.set_size(32, 18))
        ax.plot(x, y, linewidth=1)

        ax.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator())
        ax.set_xlabel('Date')
        ax.set_ylabel('Price in %s' % self.convert)

        ax.grid(True)

        fig.autofmt_xdate()

        if title is None:
            fig.suptitle(self.coin.capitalize() + ' ' + self.obs_title + ' ' + self.offset_title, fontweight="bold")
        else:
            fig.suptitle(title, fontweight="bold")

        plt.show()

    def design_bar_plot(self):
        pass

    def design_multi_lines_plot(self, title, header, data_array, dates):
        plt.style.use(self.style)
        fig, ax = plt.subplots(figsize=utils.set_size(32, 18))

        ax.set_xlabel('Date')
        ax.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator())
        ax.grid(True)

        if self.correlation:
            color = 'tab:red'
            ax.set_ylabel(header[0] + ' price in %s' % self.convert, color=color)
            ax.plot(dates, data_array[0], color=color, linewidth=1)
            ax.tick_params(axis='y', labelcolor=color)

            ax1 = ax.twinx()

            color = 'tab:blue'
            ax1.set_ylabel(header[1] + ' price in %s' % self.convert, color=color)
            ax1.plot(dates, data_array[1], color=color, linewidth=1)
            ax1.tick_params(axis='y', labelcolor=color)

        else:
            for y in data_array:
                ax.plot(dates, y, linewidth=1)
                ax.set_ylabel('Price in %s' % self.convert)
            plt.legend(header, loc='best')

        fig.autofmt_xdate()

        if title is None:
            fig.suptitle(self.coin.capitalize() + ' ' + self.obs_title + ' ' + self.offset_title, fontweight="bold")
        else:
            fig.suptitle(title, fontweight="bold")

        plt.show()
