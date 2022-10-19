import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
import talib
import numpy as np
import pandas as pd
import time

key = "<key here>"
secret = "<secret here>"

um_futures_client = UMFutures(key=key, secret=secret)
path = 'output.txt'
t = 0
while(True):
    
    if(t%12 == 0):
        print(time.ctime())
    t+=1
    close = []
    length = 1000
    try:
        info = um_futures_client.mark_price_klines("BNBUSDT", "15m", **{"limit": length})
    except:
        print('error on get klines')
        time.sleep(300)
        continue

    for i in range(0,length-1):
        close.append(float(info[i][4]))
        
    close = np.array(close)

    RSI = pd.Series(talib.RSI(close, timeperiod=14))
    LLV= RSI.rolling(window=14).min()
    HHV= RSI.rolling(window=14).max()
    stochRSI = (RSI  - LLV) / (HHV - LLV) * 100
    k = talib.SMA(np.array(stochRSI)  , 3)
    d = talib.SMA(np.array(k), 3)
    signal = "NONE"
    if(len(um_futures_client.get_orders(symbol="BNBUSDT", recvWindow=2000)) == 0):
        if(k[-2] > 80 and d[-2] > 80):
            if(k[-1] < k[-2] and d[-1] < d[-2]):
                response = um_futures_client.account(recvWindow=6000)
                logging.info(response)
                remain = float(response['totalMarginBalance'])
                price = float(um_futures_client.ticker_price("BNBUSDT")['price'])
                buy = remain*10/price
                um_futures_client.new_order(
                    
                    symbol="BNBUSDT",
                    side="SELL",
                    type="MARKET",
                    quantity=round(buy+0.005, 2)
                )
                
                um_futures_client.new_order(
                    symbol="BNBUSDT",
                    side="BUY",
                    type="STOP_MARKET",
                    closePosition = True,
                    stopPrice = round(price*1.02, 3)
                )
                
                um_futures_client.new_order(
                    symbol="BNBUSDT",
                    side="BUY",
                    type="TAKE_PROFIT_MARKET",
                    closePosition = True,
                    stopPrice = round(price*0.9969, 3)
                )
                print("SELL")
                signal = "SELL"
                time.sleep(900)
        if(k[-2] < 20 and d[-2] < 20 ):
            if(k[-1] > k[-2] and d[-1] > d[-2]):
                response = um_futures_client.account(recvWindow=6000)
                logging.info(response)
                remain = float(response['totalMarginBalance'])
                price = float(um_futures_client.ticker_price("BNBUSDT")['price'])
                buy = remain*10/price
                um_futures_client.new_order(
                    
                    symbol="BNBUSDT",
                    side="BUY",
                    type="MARKET",
                    quantity=round(buy+0.005, 2)
                )
                
                um_futures_client.new_order(
                    symbol="BNBUSDT",
                    side="SELL",
                    type="STOP_MARKET",
                    closePosition = True,
                    stopPrice = round(price*0.98, 3)
                )
                
                um_futures_client.new_order(
                    symbol="BNBUSDT",
                    side="SELL",
                    type="TAKE_PROFIT_MARKET",
                    closePosition = True,
                    stopPrice = round(price*1.0031, 3)
                )

                print("BUY")

                time.sleep(900)
    if(len(um_futures_client.get_orders(symbol="BNBUSDT", recvWindow=2000)) == 1):
        path = 'output.txt'
        f = open(path, 'a') 
        if(um_futures_client.get_orders(symbol="BNBUSDT", recvWindow=2000)[0]['type'] == 'STOP_MARKET'):
            print('make money~~~')
            now = str(time.ctime())
            now = now + '  make money~~~\n'
            f.write(now)
        else:
            print('loss money...')
            now = str(time.ctime())
            now = now + '  loss money...\n'
            f.write(now)
        f.close()
            
        um_futures_client.cancel_open_orders(symbol="BNBUSDT", recvWindow=2000)
        
    
    time.sleep(300)

