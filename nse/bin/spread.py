import pandas as pd
import numpy as np
import time
from pyfinance.ols import PandasRollingOLS
import pairTrader
import get_futures

def get_spread(data):
    spread = pd.DataFrame()
    XStock = list(data)[0]
    YStock = list(data)[1]
    pairs = YStock+'-'+XStock
    model = PandasRollingOLS(y=data[YStock], x=data[XStock], window=50)
    spread[pairs] = data[YStock] - model.beta['feature1']*data[XStock]
    spread.dropna(inplace=True)
    return spread

def get_zscore(spread, w=40):
    std = spread.rolling(center=False, window= w).std()
    mean = spread.rolling(center=False, window = w).mean()
    x = spread.rolling(center=False, window=1).mean()
    zscore = (x - mean)/std
    zscore.dropna(inplace=True)
    return zscore

#while True:
data = pd.read_csv('C:\Users\\abhi\Documents\projects\\test\data\\20181022\\banknifty_20181022.csv')
print data
    #spread = get_spread(data)
    #print(get_zscore(spread))
    #time.sleep(30*60)




























