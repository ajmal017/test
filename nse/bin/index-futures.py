"""
Author: Abhishek Chaturvedi
Date: Aug/25/2017
Description: Download NIFTY/BANKNIFTY historical data for the last 30
			days and save them in Excel format.
"""
import datetime as dt
from datetime import timedelta
import pandas as pd, seaborn as sns
from pandas import ExcelWriter
from nsepy import get_history
from datetime import date
import calendar, os
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-darkgrid')
pd.set_option('display.notebook_repr_html', True)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 10)
pd.set_option('display.width', 100)
pd.set_option('precision', 3)

symbol="NIFTY"

s = dt.datetime.today() - timedelta(days=28)
s = dt.date(2017,7,28)
y = s.year
m = s.month
d = s.day
sep = dt.date(2017,9,28)
aug = dt.date(2017,8,31)
jul = dt.date(2017,7,26)
jun = dt.date(2017,6,29)
may = dt.date(2017,5,25)

current_ed = aug
mid_ed = sep

def main():
    format = '%d%m%Y'
    todays_date = dt.date.today().strftime(format)
    directory = 'C:\\Users\\abhishek\\PycharmProjects\\test\\data\\%s' % todays_date
    if not os.path.exists(directory):
        os.makedirs(directory)
    #if not os.path.isfile(directory+'\\%s_current.xlsx' % symbol):
    current = get_history(symbol=symbol,start=date(y,m,d), end=date.today(),
                           index=True,futures=True,
                           expiry_date=current_ed)
    writer_c = ExcelWriter(directory+'\\%s_current.xlsx' % symbol)
    current.to_excel(writer_c, '%s_current' % (symbol))
    writer_c.save()
    #current.to_csv(directory+'\\%s_current.csv' % symbol)
    mid = get_history(symbol=symbol,start=date(y,m,d), end=date.today(),
                           index=True,futures=True,
                           expiry_date=mid_ed)
    writer_m = ExcelWriter(directory+'\\%s_mid.xlsx' % symbol)
    mid.to_excel(writer_m, '%s_mid' % (symbol))
    writer_m.save()
    #mid.to_csv(directory+'\\%s_mid.csv' % symbol)
    print 'Created csv dump for %s at location: %s' %(symbol, directory)
    sell_price = 10086
    buy_price  = 10011.7
    lots = 150
    columns = ['Open','Close','Settle','SellSettle','BuySettle','Sell_PL','Buy_PL','PL','MTM','RunningSUM']
    diff = pd.DataFrame(columns=columns)

    diff['Date'] = diff.index
    diff['Open'] = mid['Open'] - current['Open']
    diff['Close'] = mid['Close'] - current['Close']
    diff['Settle'] = mid['Settle Price'] - current['Settle Price']
    diff['SellSettle'] = mid['Settle Price']
    diff['BuySettle'] = current['Settle Price']
    diff['Sell_PL'] = sell_price - diff.SellSettle
    diff['Buy_PL']  = diff.BuySettle - buy_price
    diff['PL'] = diff['Sell_PL'] + diff.Buy_PL
    diff['MTM'] = lots * diff.PL
    diff['RunningSUM'] = diff.MTM.cumsum()
    print 'Open Price Std DEV = ',np.std(diff.Open)
    print 'Open Price Mean =', np.mean(diff.Open)
    print 'Max Profit = ', diff.RunningSUM[-1]
    print diff.MTM
    #plt.figure()
    #diff.RunningSUM.plot(figsize=(10,8), style='g-o')
    #plt.show()
if __name__ == '__main__':
    main()