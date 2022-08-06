#
# Python Module with Class
# for Vectorized Back-testing
#
# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#
import numpy as np
import pandas as pd
from pylab import mpl, plt
plt.style.use('seaborn')
mpl.rcParams['font.family'] = 'serif'


class MomVectorBackTester(object):
    ''' Forked from py4at-04/MomVectorBackTester.py
    '''

    def __init__(self, initial_data: pd.DataFrame, amount, tc=0, verbose=True):
        """
        Parameters:
        ===========
        initial_data: pd.DataFrame
            index: Datetime, price: float
        """
        self.amount = amount
        self.tc = tc
        self.results = None
        self.raw = initial_data.copy().dropna()
        self.verbose = verbose

    def run_strategy(self, momentum: int = 1):
        ''' Back-tests the trading strategy.
        '''
        self.momentum = momentum
        data = self.raw.copy().dropna()
        data['return'] = np.log(data['price'] / data['price'].shift(1))
        data.dropna(inplace=True)
        data['position'] = np.sign(data['return'].rolling(momentum).mean())
        data['strategy'] = data['position'].shift(1) * data['return']

        # determine when a trade takes place
        data.dropna(inplace=True)
        trades = data['position'].diff().fillna(0) != 0

        # subtract transaction costs from return when trade takes place
        data['strategy'][trades] -= self.tc
        data['cum_returns'] = self.amount * \
            data['return'].cumsum().apply(np.exp)
        data['cum_strategy'] = self.amount * \
            data['strategy'].cumsum().apply(np.exp)
        self.results = data

        # absolute performance of the strategy
        absolute_perf = data['cum_strategy'].iloc[-1]

        # out-/underperformance of strategy
        out_perf = absolute_perf - data['cum_returns'].iloc[-1]

        return round(absolute_perf, 2), round(out_perf, 2)

    def optimize_parameters(self, mom_range):
        raw = []
        for momentum in range(mom_range[0], mom_range[1], mom_range[2]):
            (abs_perf, rel_perf) = self.run_strategy()

            raw.append({
                "momentum": momentum,
                "absolute_perf": abs_perf,
                "relative_perf": rel_perf
            })

        results_df = pd.DataFrame(raw)
        winner = results_df.loc[results_df['absolute_perf'].idxmax()]
        best_momentum = int(winner['momentum'])

        # re-execute winner to save thw winning results in the class
        self.run_strategy(best_momentum)

        return best_momentum, winner['absolute_perf']

    def plot_results(self):
        ''' Plots the cumulative performance of the trading strategy
        compared to the symbol.
        '''
        if self.results is None:
            print('No results to plot yet. Run a strategy.')
        else:
            title = f"Momentum {self.momentum}"
            self.results[['cum_returns', 'cum_strategy']].plot(
                title=title, figsize=(10, 6))


if __name__ == '__main__':
    raw = pd.read_csv('./input/binance-btc-usd-1m.csv',
                      index_col=0, parse_dates=True).dropna()

    print(raw.head())

    mom_bt = MomVectorBackTester(raw, 10000, verbose=False)
    (mom, perf) = mom_bt.optimize_parameters((3, 51, 10))

    print(mom)
    print(perf)
