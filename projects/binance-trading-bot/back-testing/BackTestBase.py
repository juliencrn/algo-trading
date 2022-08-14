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
    data: DateFrame
        contains input DataFrame
    result: DateFrame
        result is made by running the strategy
    statistics: DateFrame
        statistics is made after strategy

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
        self.verbose = verbose
        self.reset_strategy()
        self.get_data()

    def get_data(self, csv_file="./BTCUSDT-1m-2020-01-01_2022-08-11.csv"):
        ''' Retrieves and prepares the data.

        Arguments:
        - file: str
            path to csv file containing Date:datetime and price:float
        '''
        raw = pd.read_csv(csv_file, index_col=0, parse_dates=True).dropna()
        raw = raw.loc[(raw.index > self.start) & (raw.index < self.end)]
        raw['return'] = np.log(raw / raw.shift(1))
        self.data = raw.dropna()

    def reset_strategy(self):
        ''' Set defaults to be able to re-run a new strategy with clean input '''
        self.units = 0
        self.position = 0  # initial neutral position
        self.trades = 0  # no trades yet
        self.amount = self.initial_amount  # reset initial capital
        self.result = None
        self.statistics = None

    def plot_data(self, cols=None, data=None, title=None, figsize=None):
        ''' Generalist plotting function
        '''
        if cols is None:
            cols = ['price']
        if data is None:
            data = self.data
        if figsize is None:
            figsize = (10, 6)
        data[cols].plot(figsize=figsize, title=title)

    def plot_strategy(self):
        ''' Draw an advanced strategy chart

        Requires that self.results contains ['cum_returns', 'cum_strategy', 'cum_max'] cols
        '''
        if self.statistics is None:
            print('No statistics to plot yet. Run a strategy.')
        else:
            cols = ['cum_returns', 'cum_strategy', 'cum_max']
            is_long = self.statistics['position'] > 0
            is_short = self.statistics['position'] < 0
            min_val = self.statistics[cols].min().min()
            max_val = self.statistics[cols].max().max()
            self.statistics[cols].plot(figsize=(10, 6))
            plt.fill_between(x=self.statistics.index, y1=max_val,
                             y2=min_val, where=is_long, color="green", alpha=0.1)
            plt.fill_between(x=self.statistics.index, y1=max_val,
                             y2=min_val, where=is_short, color="red", alpha=0.1)
            plt.show()

    def calculate_statistics(self):
        ''' From self.result to self.statistics, calculate strategy statistics'''
        if self.result is None:
            print('No result to plot yet. Run a strategy.')
        else:
            raw = self.result.copy()

            # cumulative real performance
            raw['strategy'] = np.log(
                raw['valuation'] / raw['valuation'].shift(1))
            raw['cum_returns'] = raw['return'].cumsum().apply(np.exp)
            raw['cum_strategy'] = raw['strategy'].cumsum().apply(np.exp)
            # used to calc drawdown later
            raw['cum_max'] = raw['cum_strategy'].cummax()
            raw['drawdown'] = raw['cum_max'] - raw['cum_strategy']

            self.statistics = raw

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
        TODO: add `bar` parameter to show the current strategy resume in real-time
        '''
        perf = self.get_gross_rate(self.initial_amount, self.amount) * 100
        sym = self.data['price']
        sym_perf = self.get_gross_rate(sym.iloc[0], sym.iloc[-1]) * 100
        vs_sym_perf = perf - sym_perf

        print('Initial balance [$] {:.2f}'.format(self.initial_amount))
        print('Final balance   [$] {:.2f}'.format(self.amount))
        print('Net Performance [%] {:.2f}'.format(perf))
        print('Sym Performance [%] {:.2f}'.format(sym_perf))
        print('VS Sym Perform. [%] {:.2f}'.format(vs_sym_perf))
        print('Trades Executed [#] {}'.format(self.trades))

        if self.statistics is not None:
            # max and longest drawdown
            # when drawdown == 0, we are at the top
            tmp = self.statistics['drawdown'][self.statistics['drawdown'] == 0]
            drawdown_periods = (
                tmp.index[1:].to_pydatetime() - tmp.index[:-1].to_pydatetime())

            print('Max drawdown     [%] {:.2f}'.format(
                round(self.statistics['drawdown'].max() * 100, 2)))
            print('Longest drawdown [t] {}'.format(drawdown_periods.max()))

        print('=' * 55)


if __name__ == '__main__':
    bb = BackTestBase(dt.datetime(2022, 6, 1), dt.datetime(2022, 6, 7), 10000)
    print(bb.data.info())
    print(bb.data.tail())
    bb.plot_data()
    # plt.savefig('../images/back-test-base-plot.png')
