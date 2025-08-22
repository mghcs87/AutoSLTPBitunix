from .config import Config
from .http_client import HttpClient
from .account import AccountAPI
from .market import MarketAPI
from .trade import TradeAPI

class BitunixAPI:
    def __init__(self):
        self.config = Config()
        self.http_client = HttpClient(self.config)
        self.account = AccountAPI(self.http_client)
        self.market = MarketAPI(self.http_client)
        self.trade = TradeAPI(self.http_client)