import datetime as dt
from datetime import timedelta
import pandas as pd, seaborn as sns
from nsepy import get_history
from datetime import date
import calendar, os
import numpy as np
import matplotlib.pyplot as plt

symbol="SBIN"

s = dt.datetime.today() - timedelta(days=30)
y = s.year
m = s.month
d = s.day
current_ed = dt.date(2017,8,31)
mid_ed = dt.date(2017,9,28)

def main():
    format = '%d%m%Y'
    todays_date = dt.date.today().strftime(format)
    directory = 'C:\\Users\\abhishek\\PycharmProjects\\test\\data\\%s' % todays_date
    if not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.isfile(directory+'\\%s_current.csv' % symbol):
        current = pd.read_csv(directory + '\\%s_current.csv' % symbol)
        mid = pd.read_csv(directory + '\\%s_mid.csv' % symbol)
        #stock = get_history(symbol=tick,start=oTime, end=eTime)
    else:
        current = get_history(symbol=symbol,start=date(y,m,d), end=date.today(),
                               index=False,futures=True,
                               expiry_date=current_ed)
        current.to_csv(directory+'\\%s_current.csv' % symbol)
        mid = get_history(symbol=symbol,start=date(y,m,d), end=date.today(),
                               index=False,futures=True,
                               expiry_date=mid_ed)
        mid.to_csv(directory+'\\%s_mid.csv' % symbol)
    print current[['Settle Price']]
    print mid[['Settle Price']]

if __name__ == '__main__':
    main()