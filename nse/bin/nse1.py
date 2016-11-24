from nsepy import get_history, get_index_pe_history
from nsepy.archives import get_price_history
from datetime import date
import datetime
import json
import argparse
import matplotlib.pyplot as plt
from googlefinance import getQuotes
import pandas as pd
import numpy

parser = argparse.ArgumentParser(description='STOCK volatility calculator')
parser.add_argument('-s', '--stock', help='NSE stock symbol', required=True)
parser.add_argument('-d','--delta', help='Start date', required=True)
args = vars(parser.parse_args())

#sbin = get_history(symbol= args.s,
#                    start=date(2016,1,1),
#                    end=date(2016,11,18))

#Initialize

eTime = datetime.date.today()
t_delta = datetime.timedelta(days=int(args['delta']))
sTime = eTime - t_delta

#stock = get_history(symbol=args['stock'], start= sTime,  end= eTime)
#stock[['Symbol','Close']].plot()
#plt.show()
#print(sbin.op
#proxies = {'http':'proxy1.wipro.com:8080'}
df = get_history(symbol=args['stock'], start= sTime,  end= eTime)

df["Date"] = pd.to_datetime(df.index)
#print(df)

df['LReturn'] = numpy.log(df['Close']/df['Prev Close'])

Avg = numpy.average(df['LReturn'])
Stdv = numpy.std(df['LReturn'])
print("Average price : %s" % (Avg))
print("Std Dev 1D: %s" % float(Stdv) )
#cmp = getQuotes("NSE:%s" % args['stock'])
#cmpj = json.loads(cmp)
#print cmpj[0]['LastTradePrice']
print("Current MPrice: %s" % df['Close'], )
