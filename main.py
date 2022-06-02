from binance.client import Client
import time
import os
import fetchData
import threading
import bot
import json

# binance-python setup
with open('./data.json') as f:
  data = json.load(f)

api_key = data['api_key']
api_secret = data['api_secret']
client = Client(api_key, api_secret)

marginAccountData = client.get_margin_account()

cryptolist = [] 
wrongList = []

#filtering wrong cryptos
unfilteredCryptoList = data["crypto_list"]
for crypto in unfilteredCryptoList:
    if next((item for item in marginAccountData['userAssets'] if item["asset"] == crypto), None):
        cryptolist.append(crypto)
    else:
        wrongList.append(crypto)

dataCryptoList = cryptolist

#Leave only 10 cryptos
cryptolist = cryptolist[0:10]

getData = fetchData.getData()
bot = bot.runBot()

currentData = []

def getdata():
    while True:
        global currentData
        currentData = getData.getDataF(client, cryptolist)
        time.sleep(60)

def createThreads(timeframe):
    thread = threading.Thread(target=main, args=(timeframe,))
    thread.start()

def main(timeframe):
    bot.botLaunch(currentData[timeframe], timeframe, client)

# Create data thread
dataThread = threading.Thread(target=getdata)

# Run script
if __name__=='__main__':
    dataThread.start()

    time.sleep(2)
    print('\nWybierz stopień ryzyka: \n')
    print('1: Duże ryzyko (2h)')
    print('2: Średnie ryzyko (4h)')
    print('3: Małe ryzyko (1d)')
    print('4: Koniec prograu\n')
    try:
        menu = int(input(''))
        if (menu == 1):
            createThreads(2)
        elif (menu == 2):
            createThreads(4)
        elif (menu == 3):
            createThreads(24)
        elif (menu == 4):
            print("\n\n\nKoniec programu. \n \n \n")
            os.abort()
        else:
            print("\n\n\nZły wybór, spróbuj jeszcze raz. \n \n \n")
    except ValueError:
        print('Wpisany znak nie jest liczbą')
