import urllib, time, datetime
import pandas as pd
from datetime import date
import plotly.plotly as py
from plotly.tools import FigureFactory as FF
import datetime

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

        def __init__(self, symbol, interval_seconds, num_days):
            global day
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

        interval = 900 # 15 minutes
        lookback = 22
        tick = 'SBIN'
        q = GoogleIntradayQuote(tick, interval, lookback)
        print q  # print it out
        filename = '/Users/abhishek.chaturvedi/PycharmProjects/self/test/data/tick.csv'
        q.write_csv(filename)

        #dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        #df = pd.read_csv(filename, sep=',', header=None, parse_dates={'datetime': [1, 2]},
        #                date_parser=dateparse)
        #df.columns = ['Datetime', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']
        # df.index = df['Datetime']
        # df.index.name = None
        #fig = FF.create_candlestick(df.Open, df.High, df.Low, df.Close, dates=df.index)
        #fig['layout'].update({
        #    'title': 'RCOM Intraday Charts',
        #    'yaxis': {'title': 'RCOM Stock'}})
        #py.iplot(fig, filename='finance/intraday-candlestick', validate=False)
        #py.show()