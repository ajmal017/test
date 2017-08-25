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
from openpyxl import load_workbook

symbol="BANKNIFTY"

s = dt.datetime.today() - timedelta(days=28)
s = dt.date(2017,7,28)
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
    if not os.path.isfile(directory+'\\%s_current.xlsx' % symbol):
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

if __name__ == '__main__':
    main()