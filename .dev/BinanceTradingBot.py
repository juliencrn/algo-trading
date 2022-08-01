import configparser
import websocket
import pandas as pd
import json
import numpy as np
import os
import math
# import datetime
# import requests

config = configparser.ConfigParser()
env_path = "{}/env.cfg".format(os.getcwd())
config.read(env_path)

API_URL = 'https://api.binance.com/api/v3'
WS_URL = 'wss://stream.binance.us:9443/ws'


class BaseBinanceTradingBot(object):
    def __init__(self, symbol: str, interval: str, verbose=True):
        """
        Parameters
        ----------
        symbol : str
            pair of tokens, should be in uppercase (eg: BTCUSDT)
        interval : str
            tick interval: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        verbose : bool
            print more logs
        """
        self.data = pd.DataFrame()
        self.symbol = symbol
        self.interval = interval
        self.verbose = verbose

    def plot(self, cols=None):
        ''' Plots the closing prices for symbol.'''
        if cols is None:
            cols = ['price']
        self.data[cols].plot(figsize=(10, 6), title=self.symbol)

    def stream_klines(self):
        """
        Instantiate a Websocket client listening
        SYMBOL from Binance
        """
        socket = f"{WS_URL}/{self.symbol.lower()}@kline_{self.interval}"
        ws = websocket.WebSocketApp(
            socket,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        ws.run_forever()

    def on_message(self, ws, message):
        """
        Handled by websocket connection on message
        Used to append new candle/update the last candle to our DataFrame

        Note: closed candle boolean could be find at json_message['k']['x']
        """

        json_message = json.loads(message)
        candle = json_message['k']
        price = float(candle['c'])
        # time = datetime.datetime.now()
        time = pd.to_datetime(json_message['E'], unit='ms')
        candle_closed = candle['x']

        if not math.isnan(price):
            self.data = pd.concat(
                [self.data, pd.DataFrame({"price": price}, index=[time])])

            dr = self.data.resample('5s', label='right').last().ffill()
            dr['returns'] = np.log(dr['price'] / dr['price'].shift(1))

            if self.verbose:
                print(dr.tail(20))
        else:
            print("Price is NaN")

    def on_error(self, ws, error):
        """Handled by websocket connection on error"""
        print(error)

    def on_close(self):
        """Handled by websocket connection on close"""
        print("Connection closed")

    # def get_historical(self):
    #     '''
    #     Fetch historical prices from binance (klines)
    #     Prepare it and save it in self.data as a fresh new DataFrame
    #     '''

    #     # Fetch klines for binance /api
    #     try:
    #         url = f"{API_URL}/klines?symbol={self.symbol.upper()}&interval={self.interval}"
    #         data = requests.get(url).json()
    #     except requests.exceptions.RequestException as e:
    #         raise SystemExit(e)

    #     raws = []
    #     for tick in data:
    #         time = pd.to_datetime(tick[0], unit='ms')
    #         close = float(tick[4])
    #         raws.append([time, close])

    #     df = pd.DataFrame(raws, columns=['Date', 'price'])
    #     df.set_index('Date', inplace=True)
    #     df['returns'] = np.log(df['price'] / df['price'].shift(1))
    #     self.data = df.dropna()


if __name__ == '__main__':
    bot = BaseBinanceTradingBot(
        symbol="BTCUSDT",
        interval='1m'
    )
    bot.stream_klines()
