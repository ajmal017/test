import urllib2
import time
import datetime as dt
import numpy as np
import os

stockToPull = 'VEDL.NS','SBIN.NS','CAPF.NS','ONGC.NS'

def pullData(stock):
    try:
        print 'Currently trying to pull: ',stock
        print 'Current time is: ',str(dt.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=10d/csv'
        #urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=1y/csv'
        saveFileLine = '/home/abhishek/Documents/pycharm/projects/test/data/'+stock+'.csv'

        try:
            readExistingData = open(saveFileLine,'r').read()
            splitExisting = readExistingData.split('\n')
            mostRecentLine = splitExisting[-2]
            lastUnix = mostRecentLine.split(',')[0]
            print('File exists.')
        except Exception,e:
            print str(e)
            time.sleep(5)
            lastUnix = 0

        saveFile = open(saveFileLine,'a')
        sourceCode = urllib2.urlopen(urlToVisit).read()
        splitSource = sourceCode.split('\n')

        for eachLine in splitSource:
            splitLine = eachLine.split(',')
            if len(splitLine) == 6:
                if splitLine[0] > lastUnix:
                    if 'values' not in eachLine:
                        lineToWrite = eachLine+'\n'
                        saveFile.write(lineToWrite)

        saveFile.close()
        print 'Pulled: ',stock
        print 'Sleeping'
        print str(dt.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

        #Sleep time between pulling two stock data
        time.sleep(10)

    except Exception,e:
        print 'main loop',str(e)

for eachStock in stockToPull:
    pullData(eachStock)
