from BackTestLongShortBase import *


class BackTestLongShort(BackTestLongShortBase):
    def run_momentum_strategy(self, momentum: int):
        msg = f'\n\nRunning momentum strategy | {momentum} candle'
        msg += f'\nfixed costs {self.ftc} | '
        msg += f'proportional costs {self.ptc}'
        print(msg)
        print('=' * 55)

        self.reset_strategy()
        raw = self.data.copy()

        raw['momentum'] = raw['return'].rolling(momentum).mean()
        bar = 0
        for bar in range(momentum, len(raw)):
            if self.position in [0, -1]:
                if raw['momentum'].iloc[bar] > 0:
                    self.go_long(bar, amount='all')
                    self.position = 1  # long position
            if self.position in [0, 1]:
                if raw['momentum'].iloc[bar] <= 0:
                    self.go_short(bar, amount='all')
                    self.position = -1  # short position

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

    lobt = BackTestLongShort(start, end, 100000, verbose=False)

    lobt.run_momentum_strategy(1)
