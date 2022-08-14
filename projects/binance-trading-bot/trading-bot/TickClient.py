#
# Python Script
# with Tick Data Client
#
# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#
import zmq
import json
import pandas as pd
import datetime as dt

MSG_KEY = "LOGS:"

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://0.0.0.0:5555')

# Message should be in this following format:
# "LOGS:{ /* json data as string */ }"
socket.setsockopt_string(zmq.SUBSCRIBE, MSG_KEY)

df = pd.DataFrame()

while True:
    msg = socket.recv_string()
    _, raw = msg.split(MSG_KEY)
    data = json.loads(raw)
    date = dt.datetime.fromtimestamp(int(data['timestamp']))
    new_df = pd.DataFrame(data['raw'], index=[date])
    df = pd.concat([df, new_df])

    print(df.tail())
