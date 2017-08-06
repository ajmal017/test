import datetime as dt
import pandas as pd
import numpy as np
import os,sys
import matplotlib.pyplot as plt

directory = '/Users/abhishek.chaturvedi/PycharmProjects/self/test/data'
filename = 'CMVOLT_'
lookbackdays = 20
t_delta = dt.timedelta(days=lookbackdays)
eTime = dt.date.today()
oTime = eTime - t_delta
#dates = pd.date_range(start=oTime, end=eTime, freq='B').format(formatter=lambda x: x.strftime(format))
format = '%d%m%Y'

headers=['Date','Symbol','Close',
         'PrevClose','LNReturn','PrevDV','CurrentDV',
         'AnnualV']

df = pd.read_csv(directory+'/CMVOLT_31052017.csv',names=headers,skiprows=1)
basket = ['ACC','ADANIPORTS','AMBUJACEM','ASIANPAINT','AXISBANK','BAJAJ-AUTO','BANKBARODA',
'BHEL','BPCL','BHARTIARTL','BOSCHLTD','AUROPHARMA','CIPLA','COALINDIA','DRREDDY','GAIL','GRASIM',
'HCLTECH','HDFCBANK','HEROMOTOCO','HINDALCO','HINDUNILVR','HDFC','ITC','ICICIBANK','IDEA','INDUSINDBK','INFY',
'KOTAKBANK','LT','LUPIN','M&M','MARUIT','NTPC','ONGC','POWERGRID','INFRATEL','RELIANCE','SBIN',
'SUNPHARMA','TCS','TATAMOTORS','TATAPOWER','TATASTEEL','TECHM','ULTRATECH','EICHERMOT','WIPRO','YESBANK',
'ZEEL','TATAMTRDVR']
#for eachstock in basket:
#    print df[df['Symbol'] == eachstock]['Symbol']
#    print df[df['Symbol']==eachstock]['CurrentDV']

from nsepy import get_history, get_index_pe_history
import datetime
# Initialize
lookbackdays = 60
t_delta = dt.timedelta(days=lookbackdays)
eTime = dt.date.today()
oTime = eTime - t_delta
dates = pd.date_range(start=oTime, end=eTime, freq='B').format(formatter=lambda x: x.strftime(format))

#Stock history
sbin = get_history(symbol='SBIN',start=oTime, end=eTime)
sbin_fut = get_history(symbol='SBIN',start=oTime, end=eTime,
                       index=False,futures=True,
                       expiry_date=dt.date(2017,6,29))
sbin_fut.to_csv(directory+'/stock.csv')