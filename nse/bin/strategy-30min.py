import urllib, time, datetime
import pandas as pd
import plotly.plotly as py
from plotly.tools import FigureFactory as FF
import matplotlib.pyplot as plt
import numpy as np

class Quote(object):

    dateformat = '%Y-%m-%d'
    timeformat = '%H:%M:%S'

    def __init__(self):
        self.symbol=''
        self.date,self.time,self.open_,self.high,self.low,self.close,self.volume = ([] for _ in range(7))

    def append(self,dt,open_,high,low,close,volume):
        self.date.append(dt.date())
        self.time.append(dt.time())
        self.open_.append(float(open_))
        self.high.append(float(high))
        self.low.append(float(low))
        self.close.append(float(close))
        self.volume.append(float(volume))

    def to_csv(self):
        return ''.join(["{0},{1},{2},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7}\n".format(self.symbol
                ,self.date[bar].strftime(self.dateformat),self.time[bar].strftime(self.timeformat),
                self.open_[bar],self.high[bar],self.low[bar],self.close[bar],self.volume[bar])
                       for bar in range(len(self.close))])

    def write_csv(self, filename):
        with open(filename,'w') as f:
            f.write(self.to_csv())

    def read_csv(self,filename):
        self.symbol=''
        self.date,self.time,self.open_,self.high,self.low,self.close,self.volume = ([] for _ in range(7))
        for line in open(filename,'r'):
            symbol, ds, ts, open_, high, low, close, volume = line.rstrip().split(',')
            self.symbol = symbol
            dt = datetime.datetime.strptime(ds + ' ' + ts, self.dateformat + ' ' + self.timeformat)
            self.append(dt, open_, high, low, close, volume)
        return True

    def __repr__(self):
        return self.to_csv()

class GoogleIntradayQuote(Quote):
        ''' Intraday quotes from Google. Specify interval seconds and number of days '''

        def __init__(self, symbol, interval_seconds=900, num_days=22):
            super(GoogleIntradayQuote, self).__init__()
            self.symbol = symbol.upper()
            url_string = "http://www.google.com/finance/getprices?q={0}".format(self.symbol)
            url_string += "&i={0}&p={1}d&f=d,o,h,l,c,v".format(interval_seconds, num_days)
            csv = urllib.urlopen(url_string).readlines()
            for bar in xrange(7, len(csv)):
                if csv[bar].count(',') != 5: continue
                offset, close, high, low, open_, volume = csv[bar].split(',')
                if offset[0] == 'a':
                    day = float(offset[1:])
                    offset = 0
                else:
                    offset = float(offset)
                open_, high, low, close = [float(x) for x in [open_, high, low, close]]
                dt = datetime.datetime.fromtimestamp(day + (interval_seconds * offset))
                self.append(dt, open_, high, low, close, volume)

if __name__ == '__main__':

        interval_seconds = 900
        days = 30
        tick = 'SBIN'

        try:
            q = GoogleIntradayQuote(tick, interval_seconds, days)
            vix = GoogleIntradayQuote('INDIAVIX',interval_seconds, days)

        except Exception, e:
            print str(e)
            exit(1)
            #print q  # print it out
        #tickFile = '/Users/abhishek.chaturvedi/PycharmProjects/self/test/data/%s.csv' % tick
        tickFile = 'C:\\Users\\abhishek\\Downloads\\gf30min\\%s_30min.csv' %tick
        #vixFile = '/Users/abhishek.chaturvedi/PycharmProjects/self/test/data/VIX.csv'
        vixFile = 'C:\\Users\\abhishek\\Downloads\\gf30min\\VIX_30min.csv'
        q.write_csv(tickFile)
        vix.write_csv(vixFile)

        dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

        dfTick = pd.read_csv(tickFile, sep=',', header=None, parse_dates={'datetime': [1, 2]},
                         date_parser=dateparse)
        dfTick.columns = ['Datetime', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']

        dfVIX = pd.read_csv(vixFile, sep=',', header=None, parse_dates={'datetime': [1, 2]}, date_parser=dateparse)
        dfVIX.columns = ['Datetime', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']

        data = pd.DataFrame({'Stock' :
                             dfTick['Close']})
        data = data.join(pd.DataFrame({'VIX' : dfVIX['Close']}))
        data = data.fillna(method='ffill')
        print data.head()
        #data.plot(subplots=True, grid=True, style='b',figsize=(8,6))


        rets = np.log(data / data.shift(1))
        #rets.plot(subplots=True, grid=True, style='b',figsize=(10,6))
        print rets.head()

        #Regression Analysis
        xdat = rets['Stock']
        ydat = rets['VIX']
        model = pd.ols(y=ydat,x=xdat)
        print model.beta
        plt.plot(xdat, ydat, 'r.')
        ax = plt.axis()
        x = np.linspace(ax[0],ax[1]+0.01)
        plt.plot(x, model.beta[1] + model.beta[0] * x, 'b', lw=2)
        plt.grid(True)
        plt.axis('tight')
        plt.xlabel('Stock returns : %s' % tick)
        plt.ylabel('India VIX returns')
        #plt.show()
        print rets.corr()
        pd.rolling_corr(rets['Stock'], rets['VIX'], window=252).plot(grid=True, style='b')
        plt.show()