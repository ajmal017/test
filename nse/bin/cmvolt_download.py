## Computing Volatility

# Load the required modules and packages
import numpy as np
import pandas as pd
import sys, os
import csv as cs
import urllib2
import datetime as dt
import time
from termcolor import colored

#url = "https://www.nseindia.com/archives/nsccl/volt/CMVOLT_25042017.CSV"
"""csv = "/Users/abhishek.chaturvedi/Downloads/CMVOLT_21042017.CSV"
csv1 = "/Users/abhishek.chaturvedi/Downloads/CMVOLT_25042017.CSV"
csv2 = "/Users/abhishek.chaturvedi/Downloads/CMVOLT_24042017.CSV"
df = pd.read_csv(csv, names=['Date','Symbol','Close','PrevClose','Log_Ret','Prev_Log_Ret','CurrentDailyV','AnnualV'],
                 skiprows=1)
df1 = pd.read_csv(csv1, names=['Date','Symbol','Close','PrevClose','Log_Ret','Prev_Log_Ret','CurrentDailyV','AnnualV'],
                 skiprows=1)
df2 = pd.read_csv(csv2, names=['Date','Symbol','Close','PrevClose','Log_Ret','Prev_Log_Ret','CurrentDailyV','AnnualV'],
                 skiprows=1)
"""
format = '%d%m%Y'

def download(lookbackdays):

    directory = '/Users/abhishek.chaturvedi/PycharmProjects/self/test/data'
    t_delta = dt.timedelta(days=lookbackdays)
    eTime = dt.date.today()
    oTime = eTime - t_delta
    dates = pd.date_range(start=oTime, end=eTime, freq='B').format(formatter=lambda x: x.strftime(format))
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    for i in range(len(dates)):
        vDate = dates[i]
        filename = 'CMVOLT_%s.CSV' % vDate
        url = "https://www.nseindia.com/archives/nsccl/volt/%s" % filename
        req = urllib2.Request(url, headers=hdr)
        filetoopen = '%s/%s' % (directory, filename)
        try:
            page = urllib2.urlopen(req)
            content = page.read()

            if not os.path.isfile(filetoopen):
                with open(filetoopen, 'w') as f:
                    f.write(content)
                    print 'Created file: %s' % filename
                    if not ((i+1) == len(dates)):
                        print 'Sleeping for 10 seconds before downloading next file.'
                        time.sleep(10)
            else:
                print 'File already downloaded. - "%s"' % filetoopen
        except Exception,e:
            print 'It could be a NSE holiday. Nothing to download.'
            colored('It could be a NSE holiday. Nothing to download.', 'red')

        #df = pd.read_csv(sourceCode)
        #print df.head(2)


    return True

if not download(lookbackdays=20):
    print 'Download Failed.'