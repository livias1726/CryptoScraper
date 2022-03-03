from src.cryptomarket import utils, data, parser


class Graph:
    def __init__(self, coin):
        self.coin = coin

    def show_openings(self, start=utils.DEFAULT_START, end=utils.DEFAULT_END, convert=utils.DEFAULT_CONVERT):
        dataset = self._fetch_data(start, end, convert)

        # Get openings data
        op = parser.ObservablesParser(dataset, "open", 3)
        openings = op.get_observables()

        return openings

    def show_closings(self, start=utils.DEFAULT_START, end=utils.DEFAULT_END, convert=utils.DEFAULT_CONVERT):
        dataset = self._fetch_data(start, end, convert)

        # Get openings data
        op = parser.ObservablesParser(dataset, "close", 6)
        closings = op.get_observables()

        return closings

    def show_highest(self, start=utils.DEFAULT_START, end=utils.DEFAULT_END, convert=utils.DEFAULT_CONVERT):
        dataset = self._fetch_data(start, end, convert)

        # Get openings data
        op = parser.ObservablesParser(dataset, "high", 4)
        highest = op.get_observables()

        return highest

    def show_lowest(self, start=utils.DEFAULT_START, end=utils.DEFAULT_END, convert=utils.DEFAULT_CONVERT):
        dataset = self._fetch_data(start, end, convert)

        # Get openings data
        op = parser.ObservablesParser(dataset, "low", 5)
        lowest = op.get_observables()

        return lowest

    def show_volumes(self, start=utils.DEFAULT_START, end=utils.DEFAULT_END, convert=utils.DEFAULT_CONVERT):
        dataset = self._fetch_data(start, end, convert)

        # Get openings data
        op = parser.ObservablesParser(dataset, "volume", 7)
        volumes = op.get_observables()

        return volumes

    def show_show_market_caps(self, start=utils.DEFAULT_START, end=utils.DEFAULT_END, convert=utils.DEFAULT_CONVERT):
        dataset = self._fetch_data(start, end, convert)

        # Get openings data
        op = parser.ObservablesParser(dataset, "market_cap", 8)
        market_caps = op.get_observables()

        return market_caps

    def _fetch_data(self, start, end, convert):
        cmc = data.CMCHistorical(self.coin, start, end, False, convert)
        dataset = cmc.get_historical_data()

        # Discard header
        dataset = dataset[1:]

        return dataset
