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

def write_excel(dataframe = None, stock=None):
	name = 'stock_hist_%s.xlsx' % stock
	print('Writing to excel')
	writer = pd.ExcelWriter(name, engine='xlsxwriter')
	# Convert the dataframe to an XlsxWriter Excel object.
	dataframe.to_excel(writer, sheet_name=stock)
	# Close the Pandas Excel writer and output the Excel file.
	writer.save()
	print('Successfully written to %s' % name)
	
	return True
	
def main():
	parser = argparse.ArgumentParser(description='STOCK volatility calculator')
	parser.add_argument('-s', '--stock', help='NSE stock symbol', required=True)
	parser.add_argument('-d','--delta', help='Start date', required=True)
	parser.add_argument('-f','--fdelta', help='Future days for which you are hoping for')
	args = vars(parser.parse_args())

	#Initialize

	eTime = datetime.date.today()
	t_delta = datetime.timedelta(days=int(args['delta']))
	sTime = eTime - t_delta
	f_delta = datetime.timedelta(days=int(args['fdelta']))
	fTime = eTime + f_delta

	print('Fetching Last %s days of data for stock: %s' %(args['delta'], args['stock']))
	#stock = get_history(symbol=args['stock'], start= sTime,  end= eTime)
	#stock[['Symbol','Close']].plot()

	# Get the historical data 
	df = get_history(symbol=args['stock'], start= sTime, end= eTime)
	# Create a new column
	#df["Date"] = pd.to_datetime(df.index)
	#df['LReturn'].astype(float) = math.log(df['Close'].astype(float)/df['Prev Close'].astype(float))
	#df['LReturn'] = numpy.log(df['Close'].astype(int)/df['Prev Close'].astype(int))
	df['LReturn'] = np.log(df.Close) - np.log(df['Prev Close']) # http://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe
	df.append(df['LReturn'], ignore_index=True)
	
	
	#Reduce the dataframe before write
	#df_red = df[['Date','Prev Close','Close','LReturn']]
	
	l_avg = np.average(df['LReturn'])
	l_stdv = np.std(df['LReturn'])
	l_f_avg = int(args['fdelta']) * l_avg
	l_f_stdv = l_stdv * math.sqrt(int(args['fdelta']))
	
	l_upper = l_f_avg + l_f_stdv
	l_lower = l_f_avg - l_f_stdv
	#Pick up the last using -1
	lcp = df['Close'][df.index[-1]]
	
	l_u_expected = lcp * np.exp(l_upper)
	l_l_expected = lcp * np.exp(l_lower)
	
	#np.sqrt(np.abs(l_avg)) * np.sign(l_avg)
	#l_f_stdv = 
	#print("Average price : %s" % (Avg))
	#print("Std Dev 1D: %s" % float(Stdv) )
	#cmp = getQuotes("NSE:%s" % args['stock'])
	#cmpj = json.loads(cmp)
	#print cmpj[0]['LastTradePrice']
	#print("Current MPrice: %s" % df['Close'], )

	#Print the calculations


	print('\nLast Close Price for stock: %s is: %s\n' % (args['stock'],lcp))
	print('Expected Max price in %s days : %s' % (args['fdelta'],round(l_u_expected,2)))
	print('Expected Min price in %s days : %s' % (args['fdelta'],round(l_l_expected,2)))
	
	#Write to excel
	if not write_excel(stock=args['stock'], dataframe=df):
		print('Could not write successfully. Exiting')
		exit()
	
if __name__ == "__main__":
    # execute only if run as a script
    main()
