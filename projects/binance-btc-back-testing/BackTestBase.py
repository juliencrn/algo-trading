#
# Python Script with Base Class
# for Event-Based Back-testing
#
import os
import numpy as np
import pandas as pd
import datetime as dt
from pylab import mpl, plt
plt.style.use('seaborn')
mpl.rcParams['font.family'] = 'serif'


class BackTestBase(object):
    ''' Base class for event-based back-testing of trading strategies.

    Attributes
    ==========
    start: datetime
        start date for data selection
    end: datetime
        end date for data selection
    amount: float
        amount to be invested either once or per trade
    ftc: float
        fixed transaction costs per trade (buy or sell)
    ptc: float
        proportional transaction costs per trade (buy or sell)

    Methods
    =======
    get_data:
        retrieves and prepares the base data set
    plot_data:
        plots the closing price for the symbol
    get_date_price:
        returns the date and price for the given bar
    print_balance:
        prints out the current (cash) balance
    print_net_wealth:
        prints out the current net wealth
    place_buy_order:
        places a buy order
    place_sell_order:
        places a sell order
    close_out:
        closes out a long or short position
    '''

    def __init__(self, start, end, amount,
                 ftc=0.0, ptc=0.0, verbose=True):
        self.start = start
        self.end = end
        self.initial_amount = amount
        self.amount = amount
        self.ftc = ftc
        self.ptc = ptc
        self.units = 0
        self.position = 0
        self.trades = 0
        self.verbose = verbose
        # file should have a Date:datetime and price:float
        self.data_file = "./BTCUSDT-1m.csv"
        self.get_data()
        self.result = None

    def get_data(self):
        ''' Retrieves and prepares the data.
        '''
        file = self.data_file
        raw = pd.read_csv(file, index_col=0, parse_dates=True).dropna()
        raw = raw.loc[(raw.index > self.start) & (raw.index < self.end)]
        raw['return'] = np.log(raw / raw.shift(1))
        self.data = raw.dropna()

    def plot_data(self, cols=None, data=None, title=None, figsize=None):
        ''' Plots the closing prices for symbol.
        '''
        if cols is None:
            cols = ['price']
        if data is None:
            data = self.data
        if figsize is None:
            figsize = (10, 6)
        data[cols].plot(figsize=figsize, title=title)

    def get_date_price(self, bar: int):
        ''' Return date and price for bar.
        '''
        date = self.data.index[bar]
        price = self.data.price.iloc[bar]
        return date, price

    def print_balance(self, bar: int):
        ''' Print out current cash balance info.
        '''
        date, price = self.get_date_price(bar)
        print(f'{date} | current balance {self.amount:.2f}')

    def print_net_wealth(self, bar):
        ''' Print out current cash balance info.
        '''
        date, price = self.get_date_price(bar)
        net_wealth = self.units * price + self.amount
        print(f'{date} | current net wealth {net_wealth:.2f}')

    def place_buy_order(self, bar, units=None, amount=None):
        ''' Place a buy order.
        '''
        date, price = self.get_date_price(bar)
        if units is None:
            units = int(amount / price)
        self.amount -= (units * price) * (1 + self.ptc) + self.ftc
        self.units += units
        self.trades += 1
        if self.verbose:
            print(f'{date} | buying {units} units at {price:.2f}')
            self.print_balance(bar)
            self.print_net_wealth(bar)

    def place_sell_order(self, bar, units=None, amount=None):
        ''' Place a sell order.
        '''
        date, price = self.get_date_price(bar)
        if units is None:
            units = int(amount / price)
        self.amount += (units * price) * (1 - self.ptc) - self.ftc
        self.units -= units
        self.trades += 1
        if self.verbose:
            print(f'{date} | selling {units} units at {price:.2f}')
            self.print_balance(bar)
            self.print_net_wealth(bar)

    def close_out(self, bar):
        ''' Closing out a long or short position.
        '''
        date, price = self.get_date_price(bar)
        self.amount += self.units * price
        self.units = 0
        self.trades += 1
        if self.verbose:
            print(f'{date} | closing trading at {self.amount:.2f}')
            print('=' * 55)

    def get_gross_rate(self, initial: int, final: int) -> float:
        return (final - initial) / initial

    def print_strategy_resume(self):
        ''' Print final balance, performance and others metrics

        Note: Should be called after close_out()
        '''
        perf = self.get_gross_rate(self.initial_amount, self.amount) * 100
        sym = self.data['price']
        sym_perf = self.get_gross_rate(sym.iloc[0], sym.iloc[-1]) * 100
        vs_sym_perf = perf - sym_perf

        print('Final balance   [$] {:.2f}'.format(self.amount))
        print('Net Performance [%] {:.2f}'.format(perf))
        print('Sym Performance [%] {:.2f}'.format(sym_perf))
        print('VS Sym Perform. [%] {:.2f}'.format(vs_sym_perf))
        print('Trades Executed [#] {}'.format(self.trades))
        print('=' * 55)


if __name__ == '__main__':
    bb = BackTestBase(dt.datetime(2022, 6, 1), dt.datetime(2022, 6, 7), 10000)
    print(bb.data.info())
    print(bb.data.tail())
    bb.plot_data()
    # plt.savefig('../images/back-test-base-plot.png')
