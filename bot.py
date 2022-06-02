import time
from binance.client import Client
import math
import threading
import json

with open('./data.json') as f:
  credentials = json.load(f)

api_key = credentials['api_key']
api_secret = credentials['api_secret']
client = Client(api_key, api_secret)

BUY_TRESHOLD = 40
SELL_TRESHOLD = 40

currentHoldList = []

def sellCrypto(client, symbol):
    symbolName = symbol + 'USDT'
    minQuantity = client.get_symbol_info(symbolName)["filters"][2]["minQty"]
    stepSize = client.get_symbol_info(symbolName)["filters"][2]["stepSize"]
    if next((item for item in client.get_margin_account()['userAssets'] if item["asset"] == 'BTC'), None):
        asset = next((item for item in client.get_margin_account()['userAssets'] if item["asset"] == 'BTC'))

    if float(asset['free']) >= float(minQuantity):
        rquantity = round(math.floor(float(asset['free'])/float(stepSize))*float(stepSize), 10)
        client.create_margin_order(
            symbol=symbolName,
            side="SELL",
            type="MARKET",
            quantity=rquantity
        )
        time.sleep(5)
        repayMargin(client)
        print("Sold ", rquantity, " of ", symbol)
    else:
        print("Not enough free ", symbol)

def buyCrypto(client):
    borrowMargin(client)
    time.sleep(5)

    currentBalance = float(next(item for item in client.get_margin_account()['userAssets'] if item["asset"] == 'USDT')['free'])
    stepSize = client.get_symbol_info('BTCUSDT')["filters"][2]["stepSize"]

    if currentBalance > BUY_TRESHOLD:
        currentBuy = currentBalance / float(client.get_avg_price(symbol='BTCUSDT')['price'])
        rquantity = round(math.floor(currentBuy/float(stepSize))*float(stepSize), 10)
        client.create_margin_order(
            symbol='BTCUSDT',
            side="BUY",
            type="MARKET",
            quantity=rquantity
        )

def borrowMargin(client):
    maxLoan = round(math.floor(float(client.get_max_margin_loan(asset='USDT')['amount']) * 100) / 100, 2)
    if maxLoan > BUY_TRESHOLD:
        client.create_margin_loan(asset='USDT', amount=maxLoan)
    
def repayMargin(client):
    userAssets = client.get_margin_account()["userAssets"]
    for asset in userAssets:
        if asset['asset'] == "USDT" and asset["free"] > asset["borrowed"] and asset["borrowed"] > 1:
            client.repay_margin_loan(asset='USDT', amount=float(asset['borrowed']))
        elif asset['asset'] == "USDT" and asset["borrowed"] > 1:
            client.repay_margin_loan(asset='USDT', amount=float(asset['free']))

def checkBuy(df):
    #current
    c_span_a = df["senkou_span_a"][len(df) - 1]
    c_span_b = df["senkou_span_b"][len(df) - 1]
    c_close_price = df["Close"][len(df) - 1]
    
    #previous
    p_span_a = df["senkou_span_a"][len(df) - 2]
    p_span_b = df["senkou_span_b"][len(df) - 2]
    p_close_price = df["Close"][len(df) - 2]

    if c_span_a > c_span_b and p_span_a > p_span_b and p_close_price > p_span_a and c_close_price > c_span_a: 
        return "Buy"
    elif c_span_a > c_span_b and p_span_a > p_span_b and p_close_price > p_span_a and c_close_price < c_span_a:
        return "Current price to low"
    elif c_span_a > c_span_b and p_span_a > p_span_b and p_close_price < p_span_a and c_close_price > c_span_a:
        return "Previous price to low"
    elif c_span_a > c_span_b and p_span_a > p_span_b and p_close_price < p_span_a and c_close_price < c_span_a:
        return "Current and previous price to low"
    elif c_span_a < c_span_b and p_span_a > p_span_b:
        return "Current Span A is lower then Span B"
    elif c_span_a > c_span_b and p_span_a < p_span_b:
        return "Previous Span A is lower then Span B"
    elif c_span_a < c_span_b and p_span_a < p_span_b:
        return "Current and previous Span A is lower then Span B"

def handleSell(client, asset, timeframe, df):
    print("Sell thread started: ",asset)
    time.sleep(timeframe*60)
    if checkBuy(df) != "Buy":
        sellCrypto(client, asset)

def createThreads(timeframe, df):
    holdThread = threading.Thread(target=runTime().handleHold, args=(client, timeframe, df))
    holdThread.start()
    buyThread = threading.Thread(target=runTime().handleBuy, args=(client, df,))
    buyThread.start()

class runTime:
    def handleHold(self, client, timeframe, df):
        global currentHoldList
        userAssets = client.get_margin_account()["userAssets"]
        for asset in userAssets:
            if float(asset['free']) > 0 and asset['asset'] != "USDT" and asset['asset'] != 'BNB':
                currentHoldList.append(asset['asset'])
        while True:
            # global currentHoldList
            userAssets = client.get_margin_account()["userAssets"]

            # Checking if there is any asset in the account and if there is it is adding it to the list.
            currentHoldList = []
            for asset in userAssets:
                if float(asset['free']) > 0 and asset['asset'] != "USDT" and asset['asset'] != 'BNB':
                    currentHoldList.append(asset['asset'])
            
            sellThreadList = []
            for asset in currentHoldList:
                if checkBuy(df) != "Buy":
                    sellThread = threading.Thread(target=handleSell, args=(client, asset, timeframe, df))
                    sellThread.start()
                    sellThreadList.append(sellThread)
                    currentHoldList.remove(asset)
            
            for thread in sellThreadList:
                thread.join()

            time.sleep(5)

    def handleBuy(self, client, df):
        while True:
            if checkBuy(df) == 'Buy':
                buyCrypto(client)
            time.sleep(5)

class runBot:
    def botLaunch(self, df, timeframe):
        createThreads(timeframe, df)
        while True:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            print("Current hold list: ", currentHoldList)
            print("Current status: ", checkBuy(df))
            time.sleep(timeframe*60*10)