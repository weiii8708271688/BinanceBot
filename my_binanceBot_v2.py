import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
import talib
import numpy as np
import pandas as pd
import time
import my_funtion

key = "<key here>"
secret = "<secret here>"

def deal_format(length, j, info, k):
    temp = []
    for i in range(0,length-1):
            temp.append(round(float(info[i][j]), k))
    temp = np.array(temp)
    return temp
    
klines_time = ["15m", "1h", "4h"]
sleep_time = [900, 3600]
trading_pair = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "ADAUSDT", "BNBUSDT", "DOTUSDT", "SOLUSDT", "AVAXUSDT", "MATICUSDT"]
pricePrecision = [2, 2, 4, 5, 3, 3, 4, 4, 5]
quantityPrecision = [3, 3, 1, 0, 2, 1, 0, 0, 0]

um_futures_client = UMFutures(key=key, secret=secret)
path = 'output.txt'
t = 0
Strategy = ""
while(True):
    trading = False

    if(t%12 == 0):
        print(time.strftime("%Y/%m/%d, %H:%M", time.localtime()))
    t+=1
    
    for pair in trading_pair:
        try:
            if(len(um_futures_client.get_orders(symbol=pair)) == 2 or len(um_futures_client.get_orders(symbol=pair)) == 1):
                trading = True
            time.sleep(1)
        except:
            print('error on get_orders')
            time.sleep(300)
            continue

    

    for i in range(2):
        for j in range(len(trading_pair)):
            
            length = 1000
            try:
                info = um_futures_client.mark_price_klines(trading_pair[j], klines_time[i], **{"limit": length})
                info_2 = um_futures_client.mark_price_klines(trading_pair[j], klines_time[i+1], **{"limit": length})
                nowprice = float(um_futures_client.ticker_price(trading_pair[j])['price'])
            except:
                print('error on get klines')
                time.sleep(300)
                continue

            
            
            high = deal_format(length, 2, info, pricePrecision[j])
            low = deal_format(length, 3, info, pricePrecision[j])
            close = deal_format(length, 4, info, pricePrecision[j])
            
            high_2 = deal_format(length, 2, info_2, pricePrecision[j])
            low_2 = deal_format(length, 3, info_2, pricePrecision[j])
            close_2 = deal_format(length, 4, info_2, pricePrecision[j])



            ret = my_funtion.July_01(close, high, low, close_2, info, nowprice)
            
            if(len(ret) == 0):
                ret = my_funtion.April_19(close, high, low, info, nowprice)
            
            
            
            
            
            if(len(ret) > 0 and trading == False):
                try:
                    response = um_futures_client.account(recvWindow=6000)
                    remain = float(response['totalMarginBalance'])
                    buy = remain*ret[4]/nowprice
                    um_futures_client.new_order(
                        symbol=trading_pair[j],
                        side=ret[0],
                        type="MARKET",
                        quantity=round(buy, quantityPrecision[j])
                    )
                    
                    um_futures_client.new_order(
                        symbol=trading_pair[j],
                        side=ret[3],
                        type="TAKE_PROFIT_MARKET",
                        closePosition = True,
                        stopPrice = round(ret[1], pricePrecision[j])
                    )
                    
                    um_futures_client.new_order(
                        symbol=trading_pair[j],
                        side=ret[3],
                        type="STOP_MARKET",
                        closePosition = True,
                        stopPrice = round(ret[2], pricePrecision[j])
                    )
                    
                    Strategy = ret[5]
                    path = Strategy + '.txt'
                    f = open(path, 'a')
                    now = time.strftime("%Y/%m/%d, %H:%M", time.localtime()) + ' ' + trading_pair[j] + ' ' + klines_time[i]
                    now = now + ' start the strategy\n'
                    f.write(now)
                    f.close()
                    print(time.strftime("%Y/%m/%d, %H:%M", time.localtime()) + ' ' + trading_pair[j] + ' ' + klines_time[i] + ' using ' + Strategy)
                    time.sleep(sleep_time[i])
                except ClientError as error:
                    print('error on new_orders', trading_pair[j], klines_time[i])
                    print(error.error_message)

            
            try:
                if(len(um_futures_client.get_orders(symbol=trading_pair[j], recvWindow=2000)) == 1):
                    path = Strategy + '.txt'
                    f = open(path, 'a') 
                    if(um_futures_client.get_orders(symbol=trading_pair[j], recvWindow=2000)[0]['type'] == 'STOP_MARKET'):
                        print('make money~~~')
                        now = time.strftime("%Y/%m/%d, %H:%M", time.localtime()) + ' ' + trading_pair[j] + ' ' + klines_time[i]
                        now = now + ' make money~~~\n'
                        f.write(now)
                    else:
                        print('loss money...')
                        now = time.strftime("%Y/%m/%d, %H:%M", time.localtime()) + ' ' + trading_pair[j] + ' ' + klines_time[i]
                        now = now + ' loss money...\n'
                        f.write(now)
                    f.close()
                        
                    um_futures_client.cancel_open_orders(symbol=trading_pair[j], recvWindow=2000)
            except:
                print('error on get_orders')

    ret = []
    time.sleep(300)

    

