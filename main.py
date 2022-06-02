from binance.client import Client
import time
import os
import data
import threading
import bot
import json

# binance-python setup
with open('./data.json') as f:
  credentials = json.load(f)

api_key = credentials['api_key']
api_secret = credentials['api_secret']
client = Client(api_key, api_secret)

# crypto list
cryptolist = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT', 'LTCUSDT', 'LINKUSDT', 'ICPUSDT', 'CAKEUSDT']

getData = data.getData()
bot = bot.runBot()
currentData = []
temp = []

def getdata():
    while True:
        global currentData
        currentData = getData.getDataF()

def createThreads(timeframe):
    thread = threading.Thread(target=main, args=(timeframe,))
    thread.start()

def main(timeframe):
    bot.botLaunch(currentData[timeframe]['BTCUSDT'], timeframe)

# def check():
#     while True:
#         print("Check: ",currentData[4]['BTCUSDT'].tail(1))
#         # print("Checktemp: ",temp[4])
#         time.sleep(0.1)

dataThread = threading.Thread(target=getdata)
# checkThread = threading.Thread(target=check)

# Run script
if __name__=='__main__':
    dataThread.start()
    time.sleep(5)
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
