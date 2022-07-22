#
# Python Script with Base Class
# for Event-Based Back-testing
#
# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#
import os
import numpy as np
import pandas as pd
from pylab import mpl, plt
plt.style.use('seaborn')
mpl.rcParams['font.family'] = 'serif'


class BackTestBaseYF(BackTestBase):
    ''' Base class for event-based back-testing of trading strategies.

    Attributes
    ==========
    data: DataFrame 
        date, price (close)
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

    def __init__(self, data, amount, ftc=0.0, ptc=0.0, verbose=True):
        self.initial_amount = amount
        self.amount = amount
        self.ftc = ftc
        self.ptc = ptc
        self.units = 0
        self.position = 0
        self.trades = 0
        self.verbose = verbose
        self.title = "BTC-USD Daily"
        self.prepare_data(data)

    def prepare_data(self, data):
        ''' prepares the data.
        '''
        data['return'] = np.log(data / data.shift(1))
        self.data = data.dropna()


# if __name__ == '__main__':
#     bb = BackTestBase2(data, '2010-1-1', '2019-12-31', 10000)
#     print(bb.data.info())
#     print(bb.data.tail())
#     bb.plot_data()
#     # plt.savefig('../images/back-test-base-plot.png')
