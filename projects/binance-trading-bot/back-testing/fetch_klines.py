#
# Python class that fetch klines from Binance API/
#
import numpy as np
import pandas as pd
import requests
import math
from datetime import datetime, timedelta

API_URL = 'https://api.binance.com/api/v3'


class BinanceKlines(object):
    def __init__(self, symbol="BTCUSDT", interval='1m', limit=1000, verbose=True):
        ''' 
        Parameters:
        ===========
        symbol: str
            trading pair symbol in uppercase (eg: BTCUSDT)
        interval: str
            tick interval: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        limit: int
            binance tick limit is 1000
        verbose: bool
            print logs
        '''
        self.symbol = symbol
        self.interval = interval
        self.limit = limit
        self.verbose = verbose

    def paginate_fetch(self, start: datetime, end: datetime):
        ''' Fetch klines on binance using pagination
        and returns a pd.DataFrame with a Datetime and a close price

        Note: it works for 1m time-frame only
        '''
        if start > end:
            print("Error: start datetime should be before the end datetime")
            raise

        # In 1m tick interval, 1 tick in 60 second
        time_delta = end - start
        tick_count = math.ceil(time_delta.total_seconds() / 60)
        page_count = math.ceil(tick_count / self.limit)

        if self.verbose:
            print(f"Diff: {tick_count} candles, pages: {page_count}")
            print(f'from {start} to {end}')

        klines = []
        df = pd.DataFrame()

        for i in range(0, page_count):
            # Calc pagination in ticks
            tick_start = i * self.limit
            tick_end = tick_start + self.limit - 1

            # handle the last page case
            if tick_end > tick_count:
                tick_end = tick_count

            # Convert ticks in Datetimes
            start_dt = start + timedelta(minutes=tick_start)
            end_dt = start + timedelta(minutes=tick_end)

            # fetch klines
            klines = self.fetch_klines(start_dt, end_dt)

            # extract date and price from klines
            raws = []
            for kline in klines:
                time = pd.to_datetime(kline[0], unit='ms')
                close = float(kline[4])
                raws.append([time, close])

            # concat prices in a global DataFrame
            new_df = pd.DataFrame(raws, columns=['Date', 'price'])
            new_df.set_index('Date', inplace=True)
            df = pd.concat([df, new_df])

        return df

    def fetch_klines(self, start_time: datetime, end_time: datetime):
        ''' Fetch klines on binance

        Parameters:
        ===========
        start_time, end_time: datetime
            timestamp in ms (eg: 1499783499040)

        Returns:
        ========
        klines: array
            [
                [
                    1499040000000,      // Open time
                    "0.01634790",       // Open
                    "0.80000000",       // High
                    "0.01575800",       // Low
                    "0.01577100",       // Close
                    "148976.11427815",  // Volume
                    1499644799999,      // Close time
                    "2434.19055334",    // Quote asset volume
                    308,                // Number of trades
                    "1756.87402397",    // Taker buy base asset volume
                    "28.46694368",      // Taker buy quote asset volume
                    "17928899.62484339" // Ignore.
                ]
            ]
        '''

        symbol = self.symbol.upper()
        # Binance use ms timestamp
        start_ts = int(start_time.timestamp() * 1000)
        end_ts = int(end_time.timestamp() * 1000)

        url = f"{API_URL}/klines?symbol={symbol}&interval={self.interval}&limit={self.limit}&startTime={start_ts}&endTime={end_ts}"

        try:
            data = requests.get(url).json()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        return data


if __name__ == '__main__':
    # datetime(year, month, day, hour, minute, second, microsecond)
    # start = pd.to_datetime(datetime(2022, 6, 1, 0, 0, 0))
    # end = pd.to_datetime(datetime(2022, 6, 10, 23, 59, 59))
    year = 2022
    start = datetime(year, 1, 1, 0, 0, 0)
    # end = datetime(year, 12, 31, 23, 59, 59)
    end = datetime.now()
    symbol = "BTCUSDT"
    interval = "1m"

    bk = BinanceKlines(symbol, interval, verbose=True)
    df = bk.paginate_fetch(start, end)

    # warning: this erase the prev .csv file without asking
    # df.to_csv(f"{symbol}-{interval}-{year}.csv")

    # merge files into one big
    # df_2020 = pd.read_csv(f"{symbol}-{interval}-2020.csv", parse_dates=True, index_col=0)
    # df_2021 = pd.read_csv(f"{symbol}-{interval}-2021.csv", parse_dates=True, index_col=0)
    # df_2022 = pd.read_csv(f"{symbol}-{interval}-2022.csv", parse_dates=True, index_col=0)

    # df = pd.concat([df_2020, df_2021, df_2022])

    # df.to_csv(f"{symbol}-{interval}-2020-01-01_2022-08-11.csv")
