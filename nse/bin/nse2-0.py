#!python -utt
"""
Author : Abhishek Chaturvedi
version: 2.0
"""

from nsepy import get_history, get_index_pe_history
from nsepy.archives import get_price_history
from datetime import date
import datetime
import time
import json
import argparse
import matplotlib.pyplot as plt
from googlefinance import getQuotes
import pandas as pd
import numpy as np
import math

stocksToPull = 'CAPF','SBIN','VEDL','ONGC','CUMMINSIND','PNB','BHEL','GAIL'

def bBands(price, length=30, numsd=1):
    """ returns average, upper band, and lower band"""
    ave = pd.stats.moments.rolling_mean(price, length)
    sd = pd.stats.moments.rolling_std(price, length)
    upband = ave + (sd*numsd)
    dnband = ave - (sd*numsd)
    return np.round(ave,3), np.round(upband,3), np.round(dnband,3)

def write_excel(dataframe=None, stock=None):
    #name = '/home/abhishek/Documents/pycharm/projects/data/stock_hist_%s.xlsx' % stock
    name = '/Users/abhishek.chaturvedi/PycharmProjects/self/test/data/stock_hist_%s.xlsx' % stock
    print('Writing to excel')
    writer = pd.ExcelWriter(name, engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    dataframe.to_excel(writer, sheet_name=stock)
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    print('Successfully written to %s' % name)

    return True


def get_SD(fdelta, l_avg, l_stdv,sd):
    # Calculate the projected average
    avg = float(fdelta) * float(l_avg)
    # Calculate the projected standard deviation
    stdv = math.sqrt(float(fdelta)) * float(l_stdv)
    # Calculate the projected upper and lower bounds
    upper = avg + stdv*sd
    lower = avg - stdv*sd

    return upper, lower


def yahoo_pull(stock):
    pullData(stock)
    savedFile = 'C:\Users\\abhishek\PycharmProjects\\test\\data' + stock + '.csv'
    #savedFile = '/home/abhishek/Documents/pycharm/projects/test/data/' + stock + '.csv'
    try:
        readdata = open(savedFile, 'r').read()
        splitread = readdata.split('\n')
        lastLine = splitread[-2]
        lastunixTS = lastLine.split(',')[0]
    except Exception, e:
        print 'Failed to read saved Stock file', str(e)
        exit(1)


def getcurrent(stock):
    try:
        cp = getQuotes(symbols='NSE:'+stock)
    except Exception,e:
        print 'getcurrent failed: ', str(e)

    for k, v in cp[0].items():
        if k=='LastTradePrice':
            #print 'Current Price for %s is %s.' % (stock, v)
            returnValue = float(v)

    return returnValue


def main():
    parser = argparse.ArgumentParser(description='STOCK volatility calculator')
    parser.add_argument('-c', '--current', help='Flag if current data needs to be pulled', required=False)
    parser.add_argument('-s', '--stock', help='NSE stock symbol', required=True)
    parser.add_argument('-d', '--delta', help='Start date', required=True)
    parser.add_argument('-f', '--fdelta', help='Future days for which you are hoping for', required=True)
    args = vars(parser.parse_args())

    # Initialize
    eTime = datetime.date.today()
    t_delta = datetime.timedelta(days=int(args['delta']))
    sTime = eTime - t_delta
    f_delta = datetime.timedelta(days=int(args['fdelta']))
    fTime = eTime + f_delta

    print('Fetching Last %s days of data for stock: %s' % (args['delta'], args['stock']))

    # Get the historical data
    df = get_history(symbol=args['stock'], start=sTime, end=eTime)
    df['LReturn'] = np.log(df['Close'] / df['Close'].shift(1))
    #df['LReturn'] = np.log(df.Close) - np.log(df['Prev Close']) # http://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe

    # Pick up the last using -1
    if args['current']=='C':
        lcp = getcurrent(stock=args['stock'])
    else:
        lcp = df['Close'][df.index[-1]]

    print('\nLast Close Price for stock: %s is: %s\n' % (args['stock'], lcp))

    # Calculate the average of LN returns and STDEV
    df = df.dropna()
    l_avg = np.average(df['LReturn'])
    l_stdv = np.std(df['LReturn'])

    df['Volatility'] = pd.rolling_std(df['LReturn'], window = int(args['delta'])) * np.sqrt(int(args['delta']))
    #df['Volatility'] = pd.Series(df['LReturn']).rolling(window = int(args['delta']), center=False).std()
    print('Historical Daily volatility for %s over the last %s days is : %s ' % (args['stock'],args['delta'], l_stdv))
    print('Annual Volatility for %s is: %s' %(args['stock'], round(l_stdv * np.sqrt(252) * 100 ,2)))
    #print('Daily calculated volatility: %s' % df['Volatility'].tail(22))
    # Calculate the projected price for 1SD
    l_f_upper, l_f_lower = get_SD(fdelta=float(args['fdelta']), l_avg=l_avg, l_stdv=l_stdv, sd=1)
    f_upper_expected = lcp * np.exp(l_f_upper)
    f_lower_expected = lcp * np.exp(l_f_lower)

    # Print the calculations
    print('Historical Vol~~~~')
    print('\n\t.....1SD......I am 68.27% sure about it')
    print('\tExpected Max price in %s days : %s' % (args['fdelta'], round(f_upper_expected, 2)))
    print('\tExpected Min price in %s days : %s' % (args['fdelta'], round(f_lower_expected, 2)))
    print

    # Now work for the 2SD
    l_f_upper, l_f_lower = get_SD(fdelta=args['fdelta'], l_avg=l_avg, l_stdv=l_stdv, sd=2)
    f_upper_expected = lcp * np.exp(l_f_upper)
    f_lower_expected = lcp * np.exp(l_f_lower)
    # Print the calculations
    print('\n\t.....2SD......I am 95.45% sure about it')
    print('\tExpected Max price in %s days : %s' % (args['fdelta'], round(f_upper_expected, 2)))
    print('\tExpected Min price in %s days : %s' % (args['fdelta'], round(f_lower_expected, 2)))

    # Now work on 3SD
    l_f_upper, l_f_lower = get_SD(fdelta=args['fdelta'], l_avg=l_avg, l_stdv=l_stdv, sd=3)
    f_upper_expected = lcp * np.exp(l_f_upper)
    f_lower_expected = lcp * np.exp(l_f_lower)
    # Print the calculations
    print('\n\t.....3SD......I am 99.7% sure about it')
    print('\tExpected Max price in %s days : %s' % (args['fdelta'], round(f_upper_expected, 2)))
    print('\tExpected Min price in %s days : %s' % (args['fdelta'], round(f_lower_expected, 2)))

    # Save to excel
    if not write_excel(stock=args['stock'], dataframe=df):
        print('Could not write successfully. Exiting')
        exit()

    #Visualize
    df['LReturn'].hist(figsize=(8,6), color='blue',bins=50)
    plt.show()


if __name__ == "__main__":
    # execute only if run as a script
    main()
