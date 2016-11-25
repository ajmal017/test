#!python -utt
"""
Author : Abhishek Chaturvedi
version: 0.1
"""

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

def get_1SD(fdelta=None, l_avg=None, l_stdv=None):

	# Calculate the projected average
	avg = int(fdelta) * l_avg
	# Calculate the projected standard deviation
	stdv = math.sqrt(int(fdelta)) * l_stdv
	
	# Calculate the projected upper and lower bounds
	upper = avg + stdv
	lower = avg - stdv
	
	return upper, lower
	
def get_2SD(fdelta=None, l_avg=None, l_stdv=None):
	# Calculate the projected average
	avg = int(fdelta) * l_avg
	# Calculate the projected standard deviation
	stdv = math.sqrt(int(fdelta)) * l_stdv
	
	# Calculate the projected upper and lower bounds
	upper = avg + stdv*2
	lower = avg - stdv*2
	
	return upper, lower
	
def main():
	parser = argparse.ArgumentParser(description='STOCK volatility calculator')
	parser.add_argument('-s', '--stock', help='NSE stock symbol', required=True)
	parser.add_argument('-d','--delta', help='Start date', required=True)
	parser.add_argument('-f','--fdelta', help='Future days for which you are hoping for', required = True)
	args = vars(parser.parse_args())

	#Initialize

	eTime = datetime.date.today()
	t_delta = datetime.timedelta(days=int(args['delta']))
	sTime = eTime - t_delta
	f_delta = datetime.timedelta(days=int(args['fdelta']))
	fTime = eTime + f_delta

	print('Fetching Last %s days of data for stock: %s' %(args['delta'], args['stock']))

	# Get the historical data 
	df = get_history(symbol=args['stock'], start= sTime, end= eTime)
	df['LReturn'] = np.log(df.Close) - np.log(df['Prev Close']) # http://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe

	#Pick up the last using -1
	lcp = df['Close'][df.index[-1]]
	print('\nLast Close Price for stock: %s is: %s\n' % (args['stock'],lcp))
	
	# Calculate the average of LN returns and STDEV
	l_avg 	= np.average(df['LReturn'])
	l_stdv 	= np.std(df['LReturn'])
	
	# Calculate the projected price for 1SD
	l_f_upper, l_f_lower = get_1SD(fdelta=args['fdelta'], l_avg=l_avg, l_stdv=l_stdv)
	l_u_expected = lcp * np.exp(l_f_upper)
	l_l_expected = lcp * np.exp(l_f_lower)
	
	#Print the calculations
	print('.....1SD......\n')
	print('Expected Max price in %s days : %s' % (args['fdelta'],round(l_u_expected,2)))
	print('Expected Min price in %s days : %s' % (args['fdelta'],round(l_l_expected,2)))
	print('I am 68% sure about it')
	print

	#Now work for the 2SD
	l_f_upper, l_f_lower = get_2SD(fdelta=args['fdelta'], l_avg=l_avg, l_stdv=l_stdv)
	l_u_expected = lcp * np.exp(l_f_upper)
	l_l_expected = lcp * np.exp(l_f_lower)
	#Print the calculations
	print('.....2SD......\n')
	print('Expected Max price in %s days : %s' % (args['fdelta'],round(l_u_expected,2)))
	print('Expected Min price in %s days : %s' % (args['fdelta'],round(l_l_expected,2)))
	print('I am 95% sure about it')
	#Save to excel
	if not write_excel(stock=args['stock'], dataframe=df):
		print('Could not write successfully. Exiting')
		exit()
	
if __name__ == "__main__":
    # execute only if run as a script
    main()
