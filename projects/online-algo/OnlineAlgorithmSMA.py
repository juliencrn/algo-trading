#
# Python Script
# with Online Trading Algorithm
#
# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#
import zmq
import datetime
import numpy as np
import pandas as pd

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://0.0.0.0:5555')
socket.setsockopt_string(zmq.SUBSCRIBE, 'SYMBOL')

# initial values, default empty DataFrame
# index: DateTime, columns: [price, returns, momentum], all float
df = pd.DataFrame()

# Number of tick to calc the SMAs
short_sma_len = 3
long_sma_len = 5

# Date for the next strategy calculation in ticks
min_length = long_sma_len + 1

while True:
    data = socket.recv_string()
    t = datetime.datetime.now()
    sym, value = data.split()

    df = pd.concat([df, pd.DataFrame({"price": float(value)}, index=[t])])
    dr = df.resample('5s', label='right').last()

    dr['returns'] = np.log(dr / dr.shift(1))

    if len(dr) > min_length:
        min_length += 1

        dr['short_sma'] = dr['price'].rolling(short_sma_len).mean()
        dr['long_sma'] = dr['price'].rolling(long_sma_len).mean()

        if dr['short_sma'].iloc[-2] > dr['long_sma'].iloc[-2]:
            dr['position'] = 1.0
        elif dr['short_sma'].iloc[-2] < dr['long_sma'].iloc[-2]:
            dr['position'] = -1.0
        else:
            dr['position'] = 0

        print('\n' + '=' * 51)
        print('NEW SIGNAL | {}'.format(datetime.datetime.now()))
        print('=' * 51)
        print(dr.iloc[:-1].tail())

        if dr['position'].iloc[-2] == 1.0:
            print('\nLong market position.')
            # take some action (e.g. place buy order)
        elif dr['position'].iloc[-2] == -1.0:
            print('\nShort market position.')
            # take some action (e.g. place sell order)
