#!python -utt
"""
Author : Abhishek Chaturvedi
version: 2.0
"""
#Refer:
#http://gouthamanbalaraman.com/blog/calculating-stock-beta.html

from nsepy import get_history, get_index_pe_history
from nsepy.archives import get_price_history
from datetime import date
import datetime
import time
import json
import argparse
#import matplotlib.pyplot as plt
from googlefinance import getQuotes
import pandas as pd
import numpy as np
import math
import pandas.io.data as web
import scipy.stats as stats
import pylab as plt

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


def get_SD(fdelta, l_avg, l_stdv,sd, currentPrice):
    # Calculate the projected average
    avg = float(fdelta) * float(l_avg)
    # Calculate the projected standard deviation
    stdv = math.sqrt(float(fdelta)) * float(l_stdv)
    # Calculate the projected upper and lower bounds
    upper = avg + stdv*sd
    lower = avg - stdv*sd

    f_upper_expected = currentPrice * np.exp(upper)
    f_lower_expected = currentPrice * np.exp(lower)

    stanDev = {1 : '68.27%', 2 : '95.4%', 3 : '99.7%'}
    # Print the calculations
    print('Historical Vol~~~~')
    print('\n\t.....%sSD......I am %s sure about it' %(sd, stanDev[sd]))
    print('\tExpected Max price in %s days : %s' % (fdelta, round(f_upper_expected, 2)))
    print('\tExpected Min price in %s days : %s' % (fdelta, round(f_lower_expected, 2)))


    return upper, lower


def stop_loss_HV(dailyVol, fdelta, currentPrice):

    estimated_volatility = dailyVol * np.sqrt(fdelta)
    ceiling = round(currentPrice * (1 + estimated_volatility ),2)
    floor   = round(currentPrice * (1 - estimated_volatility ),2)

    return floor, ceiling

def stop_loss_IV(dailyIV, fdelta, currentPrice):

    estimated_volatility = dailyIV * np.sqrt(fdelta)
    ceiling = round(currentPrice * ( 1 + estimated_volatility),2)
    floor = round(currentPrice * ( 1 + estimated_volatility), 2)

    return floor, ceiling

def risk_reward(postitionSize, floor, ceiling, currentPrice, long):

    if long:
        risk = (postitionSize * (currentPrice - floor))
        reward = (postitionSize * (ceiling - currentPrice))
    else:
        risk = (postitionSize * (ceiling - currentPrice))
        reward = (postitionSize * (currentPrice - floor))

    print('I stand to loose: %s' % risk)
    print('I stand to gain: %s' % reward)
    return round(risk/reward,2)


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
        cp = getQuotes(symbols=stock+'.NS')
    except Exception,e:
        print 'getcurrent failed: ', str(e)

    for k, v in cp[0].items():
        if k=='LastTradePrice':
            #print 'Current Price for %s is %s.' % (stock, v)
            returnValue = float(v)

    return returnValue

def getdata(stock, source,start,end):
    tick = stock+'.NS'
    df = web.DataReader(tick, data_source = source, start=start, end=end)

    return df

def main():
    parser = argparse.ArgumentParser(description='STOCK volatility calculator')
    parser.add_argument('-c', '--current', help='Flag if current data needs to be pulled', required=False)
    parser.add_argument('-s', '--stock', help='NSE stock symbol', required=True)
    parser.add_argument('-d', '--delta', help='Start date', required=True)
    parser.add_argument('-f', '--fdelta', help='Future days for which you are hoping for', required=True)
    parser.add_argument('-p', '--position', help='Position Size', required=True)
    parser.add_argument('-b', '--buy', help='Flag if you are buying', required=True)
    args = vars(parser.parse_args())

    # Initialize
    eTime = datetime.date.today()
    t_delta = datetime.timedelta(days=int(args['delta']))
    sTime = eTime - t_delta
    f_delta = datetime.timedelta(days=int(args['fdelta']))
    fTime = eTime + f_delta

    #long = True if args['buy'] else False
    long = False
    one_year = 365
    print('Fetching Last %s days of data for stock: %s' % (args['delta'], args['stock']))

    # Get the historical data
    #df = get_history(symbol=args['stock'], start=sTime, end=eTime)
    df = getdata(args['stock'], source='yahoo',start=sTime,end=eTime)
    #Calculate the Log Returns
    df['Log_Ret'] = np.log(df['Adj Close'] / df['Adj Close'].shift(1))
    #df['Log_Ret'] = np.log(df['Adj Close']) - np.log(df['Adj Close'].shift(1)) #http://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe

    # Pick up the last using -1
    if args['current']=='C':
        lcp = getcurrent(stock=args['stock'])
    else:
        lcp = df['Adj Close'][df.index[-1]]

    print('\nLast Close Price for stock: %s is: %s\n' % (args['stock'], lcp))

    # Calculate the average of LN returns and STDEV
    df = df.dropna()
    l_avg = np.average(df['Log_Ret'])
    l_stdv = np.std(df['Log_Ret'])

    print 'l_stdv', l_stdv
    print df['Log_Ret'].tail()

    #Calculate the rolling standard deviation of the log returns
    #df['rollingdHV'] = pd.rolling_std(df['Log_Ret'],window = int(args['delta'])) * np.sqrt(int(args['delta']))
    df['rollingdHV'] = pd.Series(df['Log_Ret']).rolling(int(args['delta'])).std() * np.sqrt(int(args['delta']))
    print df['rollingdHV'].tail(10)
    time.sleep(50)
    daily_rolling_IV = df['rollingdHV'][df.index[-1]]
    annualIV = daily_rolling_IV * np.sqrt(one_year)
    df = df['rollingdHV'].dropna()
    #df['Volatility'] = pd.Series(df['Log_Ret']).rolling(window = int(args['delta']), center=False).std()

    print('Historical Daily volatility for %s over the last %s days is : %s ' % (args['stock'],args['delta'], l_stdv))
    print('Annual Volatility for %s is: %s' % (args['stock'], round(l_stdv * np.sqrt(one_year) * 100, 2)))
    print('Daily Rolling volatility for %s over the last %s days is : %s' % (args['stock'], args['delta'], daily_rolling_IV))
    print('Daily Rolling Annual Volatility for %s is: %s' % (args['stock'], annualIV))

    # Calculate the projected price for 1SD
    for i in [1,2,3]:
        get_SD(fdelta=float(args['fdelta']), l_avg=l_avg, l_stdv=l_stdv, sd=i, currentPrice=lcp)

    floor, ceiling = stop_loss_HV(dailyVol=l_stdv, fdelta=float(args['fdelta']), currentPrice=lcp)
    print('\nSTOP LOSS Projections:')
    print('Based on the fdelta; floor of price = %s & ceiling '
          'of price = %s' % (stop_loss_HV( dailyVol=l_stdv,
                                           fdelta=float(args['fdelta']), currentPrice= lcp)))
    print('Risk:Reward = %s' %( risk_reward(postitionSize=int(args['position']),
                                            floor=floor, ceiling=ceiling, currentPrice=lcp, long=True)))

    # Save to excel
    if not write_excel(stock=args['stock'], dataframe=df):
        print('Could not write successfully. Exiting')
        exit()

    #Visualize
    #df['Log_Ret'].hist(figsize=(8,6), color='blue',bins=50)
    #Plot the Log Return
    #df['Log_Ret'].plot(grid=True).axhline(y = 0, color='black', lw=2)
    #plt.show()


if __name__ == "__main__":
    # execute only if run as a script
    main()
