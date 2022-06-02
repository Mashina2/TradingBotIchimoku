import math
from tracemalloc import start
import numpy
import time
from binance.client import Client
from datetime import datetime
import threading
import pandas as pd

api_key = "m6YdLl0Qktx64WKwD2qCFGzfqlxbs2Yji43rW1GP6JvVBAnERXjasAYjbxNEUzhH"
api_secret = "iDEBNognV3PYy2Jty0gHX1VK7DvtzRLmCBNUy0ruF3OcOKBPyD2jnK5dnrWf7sAe"
client = Client(api_key, api_secret)

# , 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT', 'LTCUSDT', 'LINKUSDT', 'ICPUSDT', 'CAKEUSDT'

symbols = ['BTCUSDT']
timeframes = [2, 4, 24]
timeframesdict = {2: Client.KLINE_INTERVAL_2HOUR, 4: Client.KLINE_INTERVAL_4HOUR, 12: Client.KLINE_INTERVAL_12HOUR, 24: Client.KLINE_INTERVAL_1DAY}

dict = {}

def getDataFrames(timeframe, startDate):
    subThreads = []
    dict[timeframe] = {}
    for symbol in symbols:
        startDate = datetime.strftime(datetime.fromtimestamp(int(time.time()) - (math.ceil((timeframe*54)/24))*86400), "%Y %m %d").replace(" ", "-")
        t = threading.Thread(target=getDataSymbols, args=(timeframe, symbol, startDate))
        t.start()
        subThreads.append(t)

    for t in subThreads:
        t.join()

def getDataSymbols(timeframe, symbol, startDate):
    fullList = numpy.array(client.get_historical_klines(symbol, timeframesdict[timeframe], startDate))
    shortList = []
    for i in fullList:
        shortList.append(i[0:5])
    shortList = numpy.array(shortList)
    dict[timeframe][str(symbol)] = calc(binanceDataFrame(shortList))

def binanceDataFrame(klines):
    df = pd.DataFrame(klines.reshape(-1,5),dtype=numpy.float64, columns = ('Open Time',
                                                                    'Open',
                                                                    'High',
                                                                    'Low',
                                                                    'Close',))
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    return df

def calc(df):
    df['tenkan_sen'] = (df['High'].rolling(window = 9).max() + df['Low'].rolling(window = 9).min()) /2
    df['kijun_sen'] = (df['High'].rolling(window=26).max() + df['Low'].rolling(window=26).min()) / 2
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(1)
    df['senkou_span_b'] = ((df['High'].rolling(window=52).max() + df['Low'].rolling(window=52).min()) / 2).shift(1)
    return df

class getData:
    def getDataF(self):
        threads = []
        for timeframe in timeframes:
            startDate = datetime.strftime(datetime.fromtimestamp(int(time.time()) - (math.ceil((timeframe*54)/24))*86400), "%Y %m %d").replace(" ", "-")
            t = threading.Thread(target=getDataFrames, args=(timeframe, startDate,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        return {2: dict[2], 4: dict[4], 24: dict[24]}
