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

#Initialize

eTime = datetime.date.today()
t_delta = datetime.timedelta(days=int(args['delta']))
sTime = eTime - t_delta

#stock = get_history(symbol=args['stock'], start= sTime,  end= eTime)
#stock[['Symbol','Close']].plot()

# Get the historical data 
df = get_history(symbol=args['stock'], start= sTime,  end= eTime)
# Create a new column
df["Date"] = pd.to_datetime(df.index)
#print(df)

df['LReturn'] = numpy.log(df['Close']/df['Prev Close'])
df1 = df.append(df['LReturn'])

#Avg = df['LReturn'].mean()
Avg = numpy.average(df['LReturn'])
Stdv = numpy.std(df['LReturn'])
print("Average price : %s" % (Avg))
print("Std Dev 1D: %s" % float(Stdv) )
#cmp = getQuotes("NSE:%s" % args['stock'])
#cmpj = json.loads(cmp)
#print cmpj[0]['LastTradePrice']
print("Current MPrice: %s" % df['Close'], )
