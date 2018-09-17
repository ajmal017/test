import numpy as np
import quandl
import pairTrader
import pandas as pd
import os
import termcolor
import datetime
import argparse

class const:
    year= 2018
    #holidays = [dt(year,1,1),dt(year,1,15),dt(year,2,19),
    #            dt(year,3,30),dt(year,5,28),dt(year,7,3),dt(year,7,4),
    #            dt(year,9,3),dt(year,11,22),dt(year,11,23),dt(year,12,24),dt(year,12,25)]
    directory = 'C:\\Users\\abhishek\\Documents\\projects\\test\\data\\usfutures\\'
    futures = ['CL','GC','QM','NG','QG']
    months = ['q','u','v','x','z']
    CL = ['clq%s' %year, 'clu%s' %year, 'clv%s' %year, 'clx%s' %year, 'clz%s' %year]
    GC = ['gcq%s' %year, 'gcu%s' %year, 'gcv%s' %year, 'gcx%s' %year, 'gcz%s' %year]
    QM = ['qmq%s' %year, 'qmu%s' %year, 'qmv%s' %year, 'qmx%s' %year, 'qmz%s' %year]
    NG = ['ngq%s' %year, 'ngu%s' %year, 'ngv%s' %year, 'ngx%s' %year, 'ngz%s' %year]
    QG = ['qgq%s' %year, 'qgu%s' %year, 'qgv%s' %year, 'qgx%s' %year, 'qgz%s' %year]
    # Create the dictionary of expiry dates for each contract
    expiry_dates = pd.Series({'CLV2018': datetime.datetime(2018, 9, 15),
                              'CLX2018': datetime.datetime(2018, 10, 15)})
    #Holidays
    #holidays = [dt(2018,1,1),dt(2018,1,15),dt(2018,2,19),
    #dt(2018,3,30),dt(2018,5,28),dt(2018,7,3),dt(2018,7,4),
    #dt(2018,9,3),dt(2018,11,22),dt(2018,11,23),dt(2018,12,24),dt(2018,12,25)]


def tocsv(data):
    filename = const.directory + data.name+'.csv'

    try:
        data.to_csv(filename)
    except Exception, e:
        print e


def main():
    parser = argparse.ArgumentParser(description='Pairs strategy for stocks')
    parser.add_argument('-d', '--delta', help='No. of days of history to pull', required=False, default=200)
    args = vars(parser.parse_args())

    # Initialize
    eTime = datetime.date.today()
    t_delta = datetime.timedelta(days=int(args['delta']))
    sTime = eTime - t_delta

    for i in range(len(const.futures)):
        print 'Futures:',const.futures[i]
        for j in range(len(const.months)):
            print 'Downloading: %s%s%s' %(const.futures[i].lower(),const.months[j].lower(),const.year)
            data = quandl.get("CME/%s%s%s"%(const.futures[i].upper(),const.months[j].upper(),const.year), authtoken="3v1zXUSUxysjyohgAQ3e",
                              start_date=sTime, end_date=eTime)
            data.name = '%s%s%s' %(const.futures[i].lower(),const.months[j].lower(),const.year)
            data.dropna()
            tocsv(data)


if __name__=="__main__":
    main()
