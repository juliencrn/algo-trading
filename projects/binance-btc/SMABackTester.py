#
# Python Module with Class
# for Vectorized Back-testing
# of SMA-based Strategies
#
# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#
import numpy as np
import pandas as pd


API_URL = 'https://api.binance.com/api/v3'


class SMABackTester(object):
    def __init__(self, initial_data: pd.DataFrame, sma1: int = 10, sma2: int = 26, verbose=True):
        """
        Parameters:
        ===========
        initial_data: pd.DataFrame
            index: Datetime, price: float, return: float
        """
        self.results = None
        self.benchmark = None
        self.update_parameters((sma1, sma2))
        self.raw = initial_data.copy().dropna()
        self.verbose = verbose

    def update_parameters(self, SMA: tuple):
        """
        Parameters:
        ===========
        SMA: tuple
            tuple of the form (sma1, sma2)
        """
        self.SMA1 = SMA[0]
        self.SMA2 = SMA[1]

    def run_strategy(self):
        data = self.raw.copy()
        data['SMA1'] = data['price'].rolling(self.SMA1).mean()
        data['SMA2'] = data['price'].rolling(self.SMA2).mean()
        data['position'] = np.where(data['SMA1'] > data['SMA2'], 1, -1)
        data['strategy'] = data['position'].shift(1) * data['return']
        data.dropna(inplace=True)
        data['cum_returns'] = data['return'].cumsum().apply(np.exp)
        data['cum_strategy'] = data['strategy'].cumsum().apply(np.exp)
        data.dropna(inplace=True)
        self.results = data

        # gross performance of the strategy
        perf = data['cum_strategy'].iloc[-1]
        # # out-/underperformance of strategy
        out_perf = perf - data['cum_returns'].iloc[-1]

        return round(perf, 2), round(out_perf, 2)

    def plot_results(self):
        ''' Plots the cumulative performance of the last trading strategy
        compared to the symbol.
        '''
        if self.results is None:
            print('No results to plot yet. Run a strategy.')
        else:
            data = self.results.copy()
            data[['cum_returns', 'cum_strategy']].plot(figsize=(12, 6))
            data[['price', 'SMA1', 'SMA2']].plot(figsize=(12, 6))
            data[['position']].plot(figsize=(12, 4), title="Positions")

    def optimize_parameters(self, SMA1_range, SMA2_range):
        ''' Finds global maximum given the SMA parameter ranges.

        Parameters
        ==========
        SMA1_range, SMA2_range: tuple
            tuples of the form (start, end, step size)

        Returns
        =======
        opt: array
            Array of winning sma pair
        strategy returns: float

        '''
        raw = []
        for sma1 in range(SMA1_range[0], SMA1_range[1], SMA1_range[2]):
            for sma2 in range(SMA2_range[0], SMA2_range[1], SMA2_range[2]):
                if sma1 >= sma2:
                    continue

                self.update_parameters((sma1, sma2))
                (perf, rel_perf) = self.run_strategy()

                raw.append({
                    "SMA1": sma1,
                    "SMA2": sma2,
                    "absolute_perf": perf,
                    "relative_perf": rel_perf
                })

        results_df = pd.DataFrame(raw)
        results_df.sort_values('absolute_perf', ascending=False, inplace=True)
        self.benchmark = results_df

        winner = results_df.loc[results_df['absolute_perf'].idxmax()]

        return (winner['SMA1'], winner['SMA2']), winner['absolute_perf']


if __name__ == '__main__':
    raw = pd.read_csv('./input/binance-btc-usd-1m.csv',
                      index_col=0, parse_dates=True).dropna()

    print(raw.head())

    sma_bt = SMABackTester(raw, verbose=False)
    (sma, perf) = sma_bt.optimize_parameters((6, 51, 2), (20, 201, 10))

    print(sma)
    print(perf)
