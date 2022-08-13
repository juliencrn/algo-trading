from turtle import position
import pandas as pd
import numpy as np
import datetime as dt
import websocket
import json
import os
import configparser
from binance.client import Client
from binance.enums import *


class OnlineTrading(object):

    def __init__(self, momentum: int = 1, testnet=True):
        self.data = pd.DataFrame()
        self.momentum = momentum
        self.position = 0
        self.min_length = momentum + 1
        self.trade_count = 0
        self.testnet = testnet
        self.position_size = 0.01  # in BTC (means almost 250 USDT)
        self.WS_URL = 'wss://stream.binance.us:9443/ws/btcusdt@kline_1m'
        self.__init_binance_client()
        self.__init_initial_balance()

        print(f"Bot initialized with {self.initial_balance} USDT")

    def __init_binance_client(self):
        config = configparser.ConfigParser()
        config.read("./env.cfg")
        mode = "testnet" if self.testnet else "mainnet"
        api_key = config[f"binance-{mode}"]["api_key"]
        api_secret = config[f"binance-{mode}"]["api_secret"]

        self.client = Client(api_key, api_secret, testnet=self.testnet)

    def __init_initial_balance(self):
        usdt = self.client.get_asset_balance(asset='USDT')

        if usdt is not None:
            self.initial_balance = float(usdt['free'])
        else:
            raise Exception("Cannot access to the initial balance")

    def run(self):
        ws = websocket.WebSocketApp(
            self.WS_URL,
            on_open=self.__on_open,
            on_message=self.__on_message,
            on_close=self.__on_close
        )
        ws.run_forever()

    def __on_open(self, ws):
        mode = "testnet" if self.testnet else "mainnet"
        print(f"Connection established (mode: {mode})")

    def __on_close(self, ws, code, msg):
        print(f"Connection closed, close position by selling out.")
        if self.position > 0:
            self.sell(self.position_size)

        self.print_balances()

    def __on_message(self, ws, message):
        data = json.loads(message)
        close = float(data['k']['c'])
        date = dt.datetime.fromtimestamp(int(int(data['E']) / 1000))
        is_candle_closed = bool(data['k']['x'])

        if is_candle_closed:
            print(f"{date}: Candle closed at {close}")

            # create & append new candle to self.data
            candle = pd.DataFrame({"price": close}, index=[date])
            candle.index.name = 'Date'
            self.data = pd.concat([self.data, candle])

            dr = self.data.resample(pd.Timedelta(1, 'm'), label='right').last()
            dr['return'] = np.log(dr['price'] / dr['price'].shift(1))
            dr['momentum'] = np.sign(
                dr['return'].rolling(self.momentum).mean())

            print(f"dr:\n {dr.tail(5)}")

            if len(dr) > self.min_length:
                if dr['momentum'].iloc[-1] > 0 and self.position == 0:
                    self.buy(self.position_size)
                elif dr['momentum'].iloc[-1] < 0 and self.position == 1:
                    self.sell(self.position_size)

    def get_gross_rate(self, initial_value: float, final_value: float) -> float:
        '''Returns the gross rate (between -1.0 to 1.0)'''
        return (final_value - initial_value) / initial_value

    def print_balances(self):
        btc = self.client.get_asset_balance(asset='BTC')
        usdt = self.client.get_asset_balance(asset='USDT')

        if btc is not None and usdt is not None:
            gross_rate = self.get_gross_rate(
                self.initial_balance, float(usdt['free']))

            print(f"Balances:")
            print(f"BTC: {btc['free']}")
            print(f"USDT (initial): {self.initial_balance}")
            print(f"USDT (current): {usdt['free']}")
            print(f"Current position: {self.position}")
            print(f"Performance: {round(gross_rate * 100, 2)}%")
            print(f"Trade count: {self.trade_count}")
        else:
            print("Error: Cannot fetch balances.")

    def buy(self, qty: float):
        ok = self.__order(SIDE_BUY, qty)
        if ok:
            self.position = 1
            print(f"Bought {qty} BTC.")
        else:
            print("Buy operation failed!")

    def sell(self, qty: float):
        ok = self.__order(SIDE_SELL, qty)
        if ok:
            self.position = 0
            print(f"Sold {qty} BTC.")
        else:
            print("Sell failed")

    def __order(self, side, qty: float) -> bool:
        ''' Place a buy or sell order
        Arguments: 
            - side: should be 'BUY' or 'SELL'
            - amount: reverse of BTC qty, it is USDT amount
        '''
        try:
            order = self.client.create_order(
                symbol='BTCUSDT',
                side=side,
                type=ORDER_TYPE_MARKET,
                # quoteOrderQty=amount,
                quantity=qty,
            )
            self.trade_count += 1

        except Exception as e:
            print(e)
            return False

        return True


if __name__ == '__main__':
    bot = OnlineTrading()
    # bot.print_balances()
    bot.run()
    # bot.buy(0.1)
    # bot.print_balances()
    # bot.sell(0.1)
    # bot.print_balances()
