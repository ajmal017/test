# Futures price calculator

from nsepy import get_history, get_index_pe_history
from nsepy.archives import get_price_history
from datetime import date
import datetime
import json
import argparse
import matplotlib.pyplot as plt
#from googlefinance import getQuotes
import pandas as pd
import numpy as np
import math

def get_future_price(stockprice=None, dte1=None, rbi_rate=None):		
	fprice = int(stockprice * (1 + rbi_rate*dte1/365 ))
	
	return fprice
		
def main():
	parser = argparse.ArgumentParser(description='STOCK volatility calculator')
	parser.add_argument('-s', '--stock', help='NSE stock symbol', required=True)
	parser.add_argument('-d','--delta', help='Start date', required=True)
	#parser.add_argument('-f','--fdelta', help='Future days for which you are hoping for', required = True)
	args = vars(parser.parse_args())

	#Initialize

	
	eTime = datetime.date.today()
	t_delta = datetime.timedelta(days=int(args['delta']))
	sTime = eTime - t_delta
	#f_delta = datetime.timedelta(days=int(args['fdelta']))
	#fTime = eTime + f_delta

	# Get the historical data 
	df = get_history(symbol=args['stock'], start= sTime, end= eTime)
	#Current price
	lcp = df['Close'][df.index[-1]]
	rbirate = float(0.058602)
	dte=22
	print('\nLast Close Price for stock: %s is: %s\n' % (args['stock'],lcp))
	print("Stock's - I: %s" % get_future_price(stockprice=lcp, dte1=dte, rbi_rate=rbirate))
	print("Stock's - I: %s" % get_future_price(stockprice=lcp, dte1=int(dte + 22), rbi_rate=rbirate))
	print("Stock's - I: %s" % get_future_price(stockprice=lcp, dte1=int(dte + 22 + 22), rbi_rate=rbirate))

if __name__ == "__main__":
    # execute only if run as a script
    main()
