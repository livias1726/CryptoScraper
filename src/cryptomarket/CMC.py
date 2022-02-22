from requests import Session
import src.cryptomarket.config as config


class CMC:
    def __init__(self, token=config.API_KEY):
        self.apiUrl = 'https://pro-api.coinmarketcap.com'
        self.headers = {'Accepts': 'application/json',
                        'X-CMC_PRO_API_KEY': token,
                        }
        self.session = Session()
        self.session.headers.update(self.headers)
