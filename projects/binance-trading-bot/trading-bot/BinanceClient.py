import configparser
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET


class BinanceClient(object):
    def __init__(self, symbol, testnet=True):
        '''
        Parameters:
        - symbol: str
            Pair symbol in uppercase like "BTCUSDT"
        '''
        config = configparser.ConfigParser()
        config.read("./env.cfg")
        mode = "testnet" if testnet else "mainnet"
        api_key = config[f"binance-{mode}"]["api_key"]
        api_secret = config[f"binance-{mode}"]["api_secret"]

        self.symbol = symbol
        self.client = Client(api_key, api_secret, testnet=testnet)

    def buy(self, qty: float):
        self.__order(SIDE_BUY, qty)

    def sell(self, qty: float):
        self.__order(SIDE_SELL, qty)

    def balance_of(self, asset) -> float:
        balance = self.client.get_asset_balance(asset=asset)
        if balance is None:
            raise Exception(f"Cannot get {asset} balance.")
        else:
            return float(balance['free'])

    def __order(self, side, qty: float):
        ''' Place a buy or sell order
        Arguments: 
            - side: should be 'BUY' or 'SELL'
            - qty: how many BTC you want to buy/sell

        return order list or raise exception
        '''
        order = self.client.create_order(
            symbol=self.symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=qty,
        )
