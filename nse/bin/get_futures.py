#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Abhishek v1.0
# Date : Aug/31/2018
# To get NIFTY individual stocks futures converted to dataframes

import nsepy
from datetime import date, datetime
import time,os
import numpy as np
import pandas as pd
import argparse
import datetime
import seaborn
import matplotlib.pyplot as plt
import pairTrader

#variables
class constants:
	pfilter = 0.05
	front_expiry = '2018,09,27'
	back_expiry = '2018,10,25'
	start_day = '2018,08,01'
	end_day = '2018,08,31'

	#timestr = time.strftime("%Y%m%d")
	timestr = "20180906"
	location = "/Users/abhishek.chaturvedi/Downloads/Rough/projects/test/data/"
	directory_name = location + timestr + '/'
	#location= "e:\\Python2.7\\projects\\test\\data\\"

	banknifty = ['AXISBANK','BANKBARODA','HDFCBANK','ICICIBANK',
				 'IDFCBANK','INDUSINDBK','KOTAKBANK',
				 'PNB','RBLBANK','SBIN','YESBANK']
	nifty50 = ['ACC','ADANIPORTS','AMBUJACEM','ASIANPAINT','AXISBANK','BAJAJ-AUTO','BANKBARODA',
	'BHEL','BPCL','BHARTIARTL','BOSCHLTD','AUROPHARMA','CIPLA','COALINDIA','DRREDDY','GAIL','GRASIM',
	'HCLTECH','HDFCBANK','HEROMOTOCO','HINDALCO','HINDUNILVR','HDFC','ITC','ICICIBANK','IDEA','INDUSINDBK','INFY',
	'KOTAKBANK','LT','LUPIN','M&M','MARUIT','NTPC','ONGC','POWERGRID','INFRATEL','RELIANCE','SBIN',
	'SUNPHARMA','TCS','TATAMOTORS','TATAPOWER','TATASTEEL','TECHM','ULTRATECH','EICHERMOT','WIPRO','YESBANK',
	'ZEEL','TATAMTRDVR']
	usfutures = ['esu18','clv18','gcz18','nqu18']
	grains = ['ZC','ZS','ZW','ZL','ZM','ZO','XK','XW','XC']
	METALS = ['GC','HG','SI','PL','PA','MGC','YG','YI']
	#ENERGY = ['BRN','NG','CL','HO','RB','QM','WBS','BZ','QG']
	ENERGY = ['cbx18','clv18','clx18']
	INDICES = ['esu18','nqu18','ymu18']
	mBasket = ['AAPL','AMD','MU','NVDA','PEP','COKE']




def convert_date(stringO):

	convertedDate = datetime.strptime(stringO, "%Y,%m,%d").date()

	return convertedDate

def get_stock_data(ticker, start_day, end_day, expiry=None):

	df = get_history(symbol=ticker,
					   start=convert_date(start_day),
					   end=convert_date(end_day))

	return df

def get_futures_data(ticker,start_day,end_day,expiry):

	if ticker == 'NIFTY':
		# Stock options (Similarly for index options, set index = True)
		df = get_history(symbol=ticker, start=convert_date(start_day),
						 end=convert_date(end_day), index=True,
						 expiry_date=convert_date(expiry))

	else:
		# Stock options (Similarly for index options, set index = True)
		df = get_history(symbol=ticker,start=convert_date(start_day),
			 			 end=convert_date(end_day),futures=True,
			 			 expiry_date=convert_date(expiry))

	print "Getting data for %s : %s" %(ticker,expiry)
	return df


def main():
	parser = argparse.ArgumentParser(description='Pairs strategy for stocks')
	parser.add_argument('-s1', '--stockY', help='NSE first stock symbol', required=False)
	parser.add_argument('-s2', '--stockX', help='NSE second stock symbol', required=False)
	parser.add_argument('-d', '--delta', help='Start date', required=False, default=200)
	parser.add_argument('-f', '--future', help='Flag for stock futures', required=False, action='store_true', default=False)
	parser.add_argument('-I', '--nifty', help='Flag for NIFTY index', required=False, action='store_true', default=False)
	parser.add_argument('-B', '--bnifty', help='Flag for BANK NIFTY index', required=False, action='store_true', default=False)
	parser.add_argument('-U', '--US', help='Flag for US Futures', required=False, action='store_true',
						default=False)
	args = vars(parser.parse_args())

	# Initialize
	eTime = datetime.date.today()
	t_delta = datetime.timedelta(days=int(args['delta']))
	sTime = eTime - t_delta

	#print('Fetching Last %s days of data' % (args['delta']))

	if args['stockY']:
		if not args['future']:
			if not args['stockX']:
				print 'Please mention second stock'
				exit(0)
		else:
			print 'Fetching futures data for stock: %s' % (args['stockY'])

	##Check if NIFTY or BANKNIFTY or US Futures has been specified
	if args['nifty']:
		name = 'nifty'
		basket = nifty50
	if args['bnifty']:
		name = 'banknifty'
		basket = banknifty
	if args['US']:
		name = 'INDICES'
		basket = constants.INDICES

	directory_name = constants.directory_name
	try:

		if not os.path.isdir(directory_name):
			os.makedirs(directory_name)
	except Exception,e:
		print e

	filename = '%s_%s.csv' % (name,constants.timestr)

	if os.path.isfile(directory_name+filename):
		print 'Data already downloaded in file: %s' %(directory_name+filename)
		try:
			data = pd.read_csv(directory_name+filename,comment='"')
			#Set Date as index
			data.set_index('Date', inplace=True)
			data.sort_values(by=['Date'],ascending=False)
		except Exception, e:
			print e
	else:
		if args['nifty'] or args['bnifty']:
			data = pairTrader.pullData(stockY=args['stockY'],stockX=args['stockX'],
				 						future=args['future'], nifty=args['nifty'],
									    bnifty=args['bnifty'],sTime=sTime,eTime=eTime,
			 							basket=basket, filename=directory_name+filename)
		else:
			data = pairTrader.usfutures(basket=basket, filename=directory_name+filename)


	# Heatmap to show the p-values of the cointegration test
	# between each pair of stocks
	"""
	scores, pvalues, pairs = pairTrader.find_cointegrated_pairs(data, pfilter)
	if pairs:
		
		print '\nPossible pair trade in the followig pairs:\n',pairs
		print 'Confidence Threshold: %s' % pfilter
		print 'Will be checking for qualifying pairs'

	else:
		print '\nNo possible pair trades found in basket : %s as pvalue of all pairs is more than %s' %(basket, pfilter)
	"""
	# Run Linear regression on all the possible pairs in basket and create a csv file
	_name = pairTrader.LRegression_allPairs(data, filename)
	# Filter the above csv file and only show qualifying trades
	pairTrader.LRegression_qualifiedPairs1(data, _name)

	""""#Seaborn Heatmap plot for pairs in the basket
	m = [0,0.2,0.4,0.6,0.8,1]
	seaborn.heatmap(pvalues, xticklabels=basket, yticklabels=basket,
		cmap='RdYlGn_r',
		mask = (pvalues >= (1.0 - pfilter)))
	plt.show()
	"""
	"""
	S1 = data['IDFCBANK']
	S2 = data['KOTAKBANK']
	score, pvalue, _ = coint(S1, S2)
	print('PValue = ',pvalue)
	ratios = S1 / S2
	ratios.plot()
	plt.axhline(ratios.mean())
	plt.legend([' Ratio'])
	plt.show()
	zscore(ratios).plot()
	plt.axhline(zscore(ratios).mean())
	plt.axhline(1.0, color='red')
	plt.axhline(-1.0, color='green')
	plt.show()
	"""

if __name__ == '__main__':
	main()