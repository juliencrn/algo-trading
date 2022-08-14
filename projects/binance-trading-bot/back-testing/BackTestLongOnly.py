from BackTestBase import *


class BackTestLongOnly(BackTestBase):
    def run_sma_strategy(self, SMA1: int, SMA2: int):
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
        self.calculate_statistics()
        self.print_strategy_resume()
        self.plot_data(['price', 'SMA1', 'SMA2'], raw)
        self.plot_strategy()

    def run_momentum_strategy(self, momentum=1):
        ''' Back-testing a momentum-based strategy.

        Parameters
        ==========
        momentum: int
            number of days for mean return calculation
        '''
        msg = f'\n\nRunning momentum strategy | {momentum} candle(s)'
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
        self.calculate_statistics()
        self.print_strategy_resume()
        self.plot_strategy()


if __name__ == '__main__':
    start = dt.datetime(2022, 6, 1)
    end = dt.datetime(2022, 6, 3)

    lobt = BackTestLongOnly(start, end, 100000, verbose=False)

    lobt.run_sma_strategy(90, 194)
    lobt.run_momentum_strategy(1)
