
import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
import talib
import numpy as np
import pandas as pd

#July_01: 【九分推薦】83%勝率，收益率935%的交易策略大公開，指標之王ADX的最強戰法#交易系統 #交易策略測試 #指標
    #https://www.youtube.com/watch?v=gfEqy4uGe8c&t=55s&ab_channel=%E6%8A%95%E6%9C%BA%E5%AE%9E%E9%AA%8C%E5%AE%A4


#April_19: 86%勝率已實測完畢，310%收益太逆天，這是能改變遊戲規則的交易策略，必看#交易系統#交易策略回測#MA均線#RSI
    #https://www.youtube.com/watch?v=X4eg-rw2hKI&t=163s&ab_channel=%E6%8A%95%E6%9C%BA%E5%AE%9E%E9%AA%8C%E5%AE%A4




def July_01(close, high, low, close_2, price, nowprice):
    adx = talib.ADX(high, low, close, 14)
    atr = talib.ATR(high, low, close, 8)
    ema = talib.EMA(close_2, 200)
    RSI = pd.Series(talib.RSI(close, timeperiod=14))
    LLV= RSI.rolling(window=14).min()
    HHV= RSI.rolling(window=14).max()
    stochRSI = (RSI  - LLV) / (HHV - LLV) * 100
    k = talib.SMA(np.array(stochRSI)  , 3)
    d = talib.SMA(np.array(k), 3)
    ret = []
    if(ema[-1] < float(price[-2][2]) and ema[-1] < float(price[-2][3]) and adx[-1] > 50 and k[-2] < d[-2] and k[-1] > d[-1]):
        ret.append("BUY")
        ret.append(nowprice + atr[-1]*1.5)
        ret.append(nowprice - atr[-1]*1.5)
        ret.append("SELL")
        ret.append(0.1*nowprice/(atr[-1]*1.5))
    elif(ema[-1] > float(price[-2][2]) and ema[-1] > float(price[-2][3]) and adx[-1] > 50 and k[-2] > d[-2] and k[-1] < d[-1]):
        ret.append("SELL")
        ret.append(nowprice - atr[-1]*1.5)
        ret.append(nowprice + atr[-1]*1.5)
        ret.append("BUY")
        ret.append(0.1*nowprice/(atr[-1]*1.5))
    if(len(ret)):
        ret.append('July_01')
    return ret




def April_19(close, high, low, price, nowprice):
    rsi = talib.RSI(close, 10)
    ma = talib.MA(close, 200)
    atr = talib.ATR(high, low, close, 14)
    ret = []
    if(ma[-1] < float(price[-2][2]) and ma[-1] < float(price[-2][3]) and rsi[-2] > 30 and rsi[-1] < 30):
        ret.append("BUY")
        ret.append(nowprice + atr[-1]*1.5)
        ret.append(nowprice - atr[-1]*1.5)
        ret.append("SELL")
        ret.append(0.1*nowprice/(atr[-1]*1.5))
    elif(ma[-1] > float(price[-2][2]) and ma[-1] > float(price[-2][3]) and rsi[-2] < 70 and rsi[-1] > 70):
        ret.append("SELL")
        ret.append(nowprice - atr[-1]*1.5)
        ret.append(nowprice + atr[-1]*1.5)
        ret.append("BUY")
        ret.append(0.1*nowprice/(atr[-1]*1.5))
    if(len(ret)):
        ret.append('April_19')
    
    return ret