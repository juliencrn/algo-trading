import pandas as pd
import numpy as np
import datetime as dt
import websocket
import zmq
import math
import json
from utils import get_gross_rate
from BinanceClient import BinanceClient


class OnlineTradingBot(object):

    def __init__(self, budget: int = 1_000, momentum: int = 1, testnet=True, verbose=True):
        self.data = pd.DataFrame()
        self.momentum = momentum
        self.position: int = 0
        self.min_length = momentum + 1
        self.trade_count = 0
        self.testnet = testnet
        self.verbose = verbose
        self.WS_URL = 'wss://stream.binance.us:9443/ws/btcusdt@kline_1m'
        self.client = BinanceClient("BTCUSDT", testnet=testnet)

        # even if we have S1M usdt, we want to trade with a budget (balance)
        initial_binance_balance = self.client.balance_of(asset='USDT')

        if budget > initial_binance_balance:
            raise Exception("Budget cannot be greater that available funds.")

        self.UNIT_SIZE = 0.01
        self.INITIAL_BALANCE = budget
        self.balance = budget
        self.BALANCE_DELTA = initial_binance_balance - budget
        self.position_size = math.floor(self.balance / self.UNIT_SIZE)

        # run a local zmq tcp service to send trading logs
        # these data could be plotted in real-time in a notebook
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind('tcp://0.0.0.0:5555')
        self.socket = socket

        if self.verbose:
            print(f"Bot initialized with {budget} USDT")

    def close_position(self):
        if self.position > 0:
            self.client.sell(self.position_size)
            self.position = 0
            self.trade_count += 1

    def run(self):
        ws = websocket.WebSocketApp(
            self.WS_URL,
            on_open=self.__on_open,
            on_message=self.__on_message,
            on_close=self.__on_close
        )
        ws.run_forever()

    def __on_open(self, ws):
        if self.verbose:
            mode = "testnet" if self.testnet else "mainnet"
            print(f"Connection established (mode: {mode})")

    def __on_close(self, ws, code, msg):
        if self.verbose:
            print(f"Connection closed, close position by selling out.")
        self.close_position()

    def __on_message(self, ws, message):
        data = json.loads(message)
        datetime = dt.datetime.fromtimestamp(int(int(data['E']) / 1000))
        price = float(data['k']['c'])
        is_candle_closed = bool(data['k']['x'])
        self.__on_data(datetime, price, is_candle_closed)

    def __on_data(self, datetime: dt.datetime, price: float, is_candle_closed: bool):
        if self.verbose:
            print("New tick:", datetime, price)
        # create & append new candle to self.data
        candle = pd.DataFrame({"price": price}, index=[datetime])
        candle.index.name = 'Date'
        self.data = pd.concat([self.data, candle])

        # prepare logs
        log = {
            "timestamp": int(datetime.timestamp()),
            "raw": {
                "price": price,
                "position": self.position,
                "balance": self.balance
            }
        }

        if is_candle_closed:
            # Calc mandatory technical indicator to be able to trade
            dr = self.data.resample(pd.Timedelta(1, 'm'), label='right').last()
            dr['return'] = np.log(dr['price'] / dr['price'].shift(1))
            dr['momentum'] = dr['return'].rolling(self.momentum).mean()

            print("is close")
            print(self.position, self.position_size,
                  self.position_size * price)

            # trade
            if len(dr) > self.min_length:
                if np.sign(dr['momentum'].iloc[-2]) > 0 and self.position == 0:
                    print("buy signal")
                    precision = 10_000
                    reserve = 100
                    available_balance = self.balance - reserve
                    self.position_size = math.floor(
                        available_balance / price * precision)/precision

                    print(f"Position size: {self.position_size}")
                    self.client.buy(self.position_size)
                    self.position = 1
                    self.trade_count += 1
                    if self.verbose:
                        print(f"Buy {self.position_size} BTC")

                elif np.sign(dr['momentum'].iloc[-2]) < 0 and self.position == 1:
                    print("sell signal")
                    self.client.sell(self.position_size)
                    self.position = 0
                    self.trade_count += 1
                    if self.verbose:
                        print(f"Sell {self.position_size} BTC")

            print("after trade")

            # update class balance
            # - from real wallet current balance
            # - including current position value (aka: un-realized profit/loss)
            wallet_balance = self.client.balance_of("USDT")
            position_value = self.position * self.position_size * price
            self.balance = wallet_balance - self.BALANCE_DELTA + position_value

            print("new balance", self.balance)

            # update log if there was a trade
            log["raw"]['position'] = self.position
            log["raw"]['balance'] = self.balance

        # send logs
        self.socket.send_string(f"LOGS:{json.dumps(log)}")

    def print_balances(self):
        usdt = self.client.balance_of(asset='USDT')
        gross_rate = get_gross_rate(self.INITIAL_BALANCE, self.balance)

        print(f"Balances:")
        print(f"Binance free USDT: {usdt}")
        print(f"Initial balance: {self.INITIAL_BALANCE}")
        print(f"Final balance: {self.balance}")
        print(f"Current position: {self.position}")
        print(f"Trade count: {self.trade_count}")
        print(f"Performance: {round(gross_rate * 100, 2)}%")


if __name__ == '__main__':
    bot = OnlineTradingBot()
    bot.run()
