#
# Python Script with Long Only Class
# for Event-based Back-testing
#
# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#
from BackTestBase import *

# Function forked from BackTestLongOnly


class BackTestLongOnly(BackTestBase):
    def reset_strategy(self):
        self.position = 0  # initial neutral position
        self.trades = 0  # no trades yet
        self.amount = self.initial_amount  # reset initial capital
        self.result = None

    def run_sma_strategy(self, SMA1, SMA2):
        ''' Back-testing a SMA-based strategy.

        Parameters
        ==========
        SMA1, SMA2: int
            shorter and longer term simple moving average (in days)
        '''
        msg = f'\n\nRunning SMA strategy | SMA1={SMA1} & SMA2={SMA2}'
        msg += f'\nfixed costs {self.ftc} | '
        msg += f'proportional costs {self.ptc}'
        print(msg)
        print('=' * 55)

        self.reset_strategy()
        raw = self.data.copy()

        raw['SMA1'] = raw['price'].rolling(SMA1).mean()
        raw['SMA2'] = raw['price'].rolling(SMA2).mean()
        raw['position'] = 0

        bar = 0
        for bar in range(SMA2, len(raw)):
            if self.position == 0:
                if raw['SMA1'].iloc[bar] > raw['SMA2'].iloc[bar]:
                    self.place_buy_order(bar, amount=self.amount)
                    self.position = 1  # long position

            elif self.position == 1:
                if raw['SMA1'].iloc[bar] < raw['SMA2'].iloc[bar]:
                    self.place_sell_order(bar, units=self.units)
                    self.position = 0  # market neutral

            # add position and balance to the DataFrame
            price = self.get_date_price(bar)[1]
            valuation = self.units * price + self.amount
            raw.at[raw.index[bar], 'valuation'] = valuation
            raw.at[raw.index[bar], 'position'] = self.position

        self.result = raw

        self.close_out(bar)
        self.calculate_strategy_stats()
        self.print_strategy_resume()
        self.plot_data(['price', 'SMA1', 'SMA2'], raw)
        self.plot_strategy()

    def plot_strategy(self):
        if self.result is None:
            print('No result to plot yet. Run a strategy.')
        else:
            cols = ['cum_returns', 'cum_strategy', 'cum_max']
            where = self.result['position'] > 0
            min_val = self.result[cols].min().min()
            max_val = self.result[cols].max().max()
            self.result[cols].plot(figsize=(10, 6))
            plt.fill_between(x=self.result.index, y1=max_val,
                             y2=min_val, where=where, color="green", alpha=0.1)
            plt.show()

    def calculate_strategy_stats(self):
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

            self.result = raw

    def print_strategy_resume(self):
        ''' Print final balance, performance and others metrics
        '''
        if self.result is None:
            print('No result to plot yet. Run a strategy.')
        else:
            perf = self.get_gross_rate(self.initial_amount, self.amount) * 100
            sym = self.result['price']
            sym_perf = self.get_gross_rate(sym.iloc[0], sym.iloc[-1]) * 100
            vs_sym_perf = perf - sym_perf

            # max and longest drawdown
            drawdown = self.result['cum_max'] - self.result['cum_strategy']
            # when drawdown == 0, we are at the top
            temp = drawdown[drawdown == 0]
            drawdown_periods = (
                temp.index[1:].to_pydatetime() - temp.index[:-1].to_pydatetime())

            print('Final balance   [$] {:.2f}'.format(self.amount))
            print('Net Performance [%] {:.2f}'.format(perf))
            print('Sym Performance [%] {:.2f}'.format(sym_perf))
            print('VS Sym Perform. [%] {:.2f}'.format(vs_sym_perf))
            print('Trades Executed [#] {}'.format(self.trades))
            print('Max drawdown    [%] {:.2f}'.format(
                round(drawdown.max() * 100, 2)))
            print('Longest drawdown    {}'.format(drawdown_periods.max()))
            print('=' * 55)

    def run_momentum_strategy(self, momentum=1):
        ''' Back-testing a momentum-based strategy.

        Parameters
        ==========
        momentum: int
            number of days for mean return calculation
        '''
        msg = f'\n\nRunning momentum strategy | {momentum} days'
        msg += f'\nfixed costs {self.ftc} | '
        msg += f'proportional costs {self.ptc}'
        print(msg)
        print('=' * 55)

        self.reset_strategy()
        raw = self.data.copy()

        raw['momentum'] = raw['return'].rolling(momentum).mean()
        raw['position'] = 0

        bar = 0
        for bar in range(momentum, len(raw)):
            if self.position == 0:
                if raw['momentum'].iloc[bar] > 0:
                    self.place_buy_order(bar, amount=self.amount)
                    self.position = 1  # long position
            elif self.position == 1:
                if raw['momentum'].iloc[bar] < 0:
                    self.place_sell_order(bar, units=self.units)
                    self.position = 0  # market neutral

            # add position and balance to the DataFrame
            price = self.get_date_price(bar)[1]
            valuation = self.units * price + self.amount
            raw.at[raw.index[bar], 'valuation'] = valuation
            raw.at[raw.index[bar], 'position'] = self.position

        self.result = raw

        self.close_out(bar)
        self.calculate_strategy_stats()
        self.print_strategy_resume()
        self.plot_strategy()


if __name__ == '__main__':
    start = dt.datetime(2022, 6, 1)
    end = dt.datetime(2022, 6, 3)

    lobt = BackTestLongOnly(start, end, 100000, verbose=False)

    lobt.run_sma_strategy(90, 194)
    lobt.run_momentum_strategy(1)
