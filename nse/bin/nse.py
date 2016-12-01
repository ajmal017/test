#!python -utt
"""
Author : Abhishek Chaturvedi
version: 0.9
"""

from nsepy import get_history, get_index_pe_history
from nsepy.archives import get_price_history
from datetime import date
import datetime
import json
import argparse
import matplotlib.pyplot as plt
from googlefinance import getQuotes
import pandas as pd
import numpy as np
import math

stocksToPull = 'CAPF','SBIN','VEDL','ONGC','CUMMINSIND','PNB','BHEL','GAIL'

def write_excel(dataframe=None, stock=None):
    name = '/home/abhishek/Documents/pycharm/projects/data/stock_hist_%s.xlsx' % stock
    print('Writing to excel')
    writer = pd.ExcelWriter(name, engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object.
    dataframe.to_excel(writer, sheet_name=stock)
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    print('Successfully written to %s' % name)

    return True


def get_SD(fdelta=None, l_avg=None, l_stdv=None,sd=None):
    # Calculate the projected average
    avg = int(fdelta) * l_avg
    # Calculate the projected standard deviation
    stdv = math.sqrt(int(fdelta)) * l_stdv

    # Calculate the projected upper and lower bounds
    upper = avg + stdv*int(sd)
    lower = avg - stdv*int(sd)

    return upper, lower


def get_2SD(fdelta=None, l_avg=None, l_stdv=None):
    # Calculate the projected average
    avg = int(fdelta) * l_avg
    # Calculate the projected standard deviation
    stdv = math.sqrt(int(fdelta)) * l_stdv

    # Calculate the projected upper and lower bounds
    upper = avg + stdv * 2
    lower = avg - stdv * 2

    return upper, lower

def get_3SD(fdelta=None, l_avg=None, l_stdv=None):
    # Calculate the projected average
    avg = int(fdelta) * l_avg
    # Calculate the projected standard deviation
    stdv = math.sqrt(int(fdelta)) * l_stdv

    # Calculate the projected upper and lower bounds
    upper = avg + stdv * 3
    lower = avg - stdv * 3

    return upper, lower


def yahoo_pull(stock):
    pullData(stock)
    savedFile = '/home/abhishek/Documents/pycharm/projects/test/data/' + stock + '.csv'
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
    df['LReturn'] = np.log(df.Close) - np.log(
        df['Prev Close'])  # http://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe

    # Pick up the last using -1
    if args['current']=='C':
        lcp = getcurrent(stock=args['stock'])
    else:
        lcp = df['Close'][df.index[-1]]

    print('\nLast Close Price for stock: %s is: %s\n' % (args['stock'], lcp))

    # Calculate the average of LN returns and STDEV
    l_avg = np.average(df['LReturn'])
    l_stdv = np.std(df['LReturn'])
    print('Daily volatility for %s is : %s ' % (args['stock'], round(l_stdv * 100, 2)))

    # Calculate the projected price for 1SD
    l_f_upper, l_f_lower = get_SD(fdelta=args['fdelta'], l_avg=l_avg, l_stdv=l_stdv, sd=1)
    l_u_expected = lcp * np.exp(l_f_upper)
    l_l_expected = lcp * np.exp(l_f_lower)

    # Print the calculations
    print('\n\t.....1SD......I am 68.27% sure about it')
    print('Expected Max price in %s days : %s' % (args['fdelta'], round(l_u_expected, 2)))
    print('Expected Min price in %s days : %s' % (args['fdelta'], round(l_l_expected, 2)))
    print

    # Now work for the 2SD
    l_f_upper, l_f_lower = get_SD(fdelta=args['fdelta'], l_avg=l_avg, l_stdv=l_stdv, sd=2)
    l_u_expected = lcp * np.exp(l_f_upper)
    l_l_expected = lcp * np.exp(l_f_lower)
    # Print the calculations
    print('\n\t.....2SD......I am 95.45% sure about it')
    print('Expected Max price in %s days : %s' % (args['fdelta'], round(l_u_expected, 2)))
    print('Expected Min price in %s days : %s' % (args['fdelta'], round(l_l_expected, 2)))

    # Now work on 3SD
    l_f_upper, l_f_lower = get_SD(fdelta=args['fdelta'], l_avg=l_avg, l_stdv=l_stdv, sd=3)
    l_u_expected = lcp * np.exp(l_f_upper)
    l_l_expected = lcp * np.exp(l_f_lower)
    # Print the calculations
    print('\n\t.....2SD......I am 99.7% sure about it')
    print('Expected Max price in %s days : %s' % (args['fdelta'], round(l_u_expected, 2)))
    print('Expected Min price in %s days : %s' % (args['fdelta'], round(l_l_expected, 2)))

    # Save to excel
    if not write_excel(stock=args['stock'], dataframe=df):
        print('Could not write successfully. Exiting')
        exit()


if __name__ == "__main__":
    # execute only if run as a script
    main()
