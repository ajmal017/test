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
from os.path import expanduser
import colorama
import platform
from statsmodels.tsa.stattools import coint
import logging

colorama.init()
#variables
class constants:
	pfilter = 0.02
	front_expiry = '2019,04,25'
	back_expiry = '2019,05,30'
	start_day = '2018,08,01'
	end_day = '2019,04,04'
	expiry_date = datetime.date(2019,04,25)
	expiry_month = 'Apr'
	timestr = time.strftime("%Y%m%d")
	script_dir = os.path.dirname(os.path.abspath(__file__))
	location = script_dir + '/../../data/'
	log_location = location + 'log/'
	directory_name = location + timestr + '/'

	current_filename = directory_name + '../open_trades/current.csv'

	index=['NIFTY','BANKNIFTY']

	niftyauto = ['AMARAJABAT','APOLLOTYRE','ASHOKLEY','BAJAJ-AUTO','BHARATFORG','BOSCHLTD','EICHERMOT','EXIDEIND',
				  'HEROMOTOCO','MRF','M&M','MARUTI','MOTHERSUMI','TVSMOTOR','TATAMTRDVR','TATAMOTORS']
	niftyit = ['HCLTECH', 'INFIBEAM', 'INFY', 'KPIT', 'MINDTREE', 'OFSS', 'TCS', 'TATAELXSI', 'TECHM', 'WIPRO']
	niftymetal = ['APLAPOLLO', 'COALINDIA', 'HINDALCO', 'HINDCOPPER', 'HINDZINC', 'JSWSTEEL',
			  'JSLHISAR', 'JINDALSTEL', 'MOIL', 'NMDC', 'NATIONALUM', 'SAIL', 'TATASTEEL', 'VEDL', 'WELCORP']
	#banknifty = ['BANKNIFTY','AXISBANK','BANKBARODA','HDFCBANK','ICICIBANK',
				 #'IDFCBANK','INDUSINDBK','KOTAKBANK',
				 #'PNB','RBLBANK','SBIN','YESBANK']
	banknifty = ['AXISBANK', 'BANKBARODA', 'HDFCBANK', 'ICICIBANK',
				 'IDFCBANK', 'INDUSINDBK', 'KOTAKBANK',
				 'PNB', 'SBIN']
	nifty50 = ['ACC','ADANIPORTS','AMBUJACEM','ASIANPAINT','AXISBANK','BAJAJ-AUTO','BANKBARODA',
	'BHEL','BPCL','BHARTIARTL','BOSCHLTD','AUROPHARMA','CIPLA','COALINDIA','DRREDDY','GAIL','GRASIM',
	'HCLTECH','HDFCBANK','HEROMOTOCO','HINDALCO','HINDUNILVR','HDFC','ITC','ICICIBANK','IDEA','INDUSINDBK','INFY',
	'KOTAKBANK','LT','LUPIN','M&M','MARUTI','NTPC','ONGC','POWERGRID','INFRATEL','RELIANCE','SBIN',
	'SUNPHARMA','TCS','TATAMOTORS','TATAPOWER','TATASTEEL','TECHM','ULTRATECH','EICHERMOT','WIPRO','YESBANK',
	'ZEEL','TATAMTRDVR']
	usfutures = ['esu18','clv18','gcz18','nqu18']
	grains = ['ZC','ZS','ZW','ZL','ZM','ZO','XK','XW','XC']
	METALS = ['GC','HG','SI','PL','PA','MGC','YG','YI']
	#ENERGY = ['BRN','NG','CL','HO','RB','QM','WBS','BZ','QG']
	ENERGY = ['cbx18','clv18','clx18']
	INDICES = ['esu18','nqu18','ymu18']
	mBasket = ['AAPL','AMD','MU','NVDA','PEP','COKE']
	bnifty_lotsize = {'AXISBANK':1200, 'BANKBARODA': 4000,'HDFCBANK':500,'ICICIBANK':2750,
					  'IDFCBANK':11000,'INDUSINDBK':300,'KOTAKBANK': 800,'PNB':5500,'RBLBANK':1200,
					  'SBIN':3000,'YESBANK':1750,'BANKNIFTY':40}
	header = ['YStock', 'XStock', 'PValue', 'Beta', 'STD_ERR_Ratio', 'Alpha', 'Close_STD_Error', 'Alpha:YPrice']


def get_stock_data(ticker, start_day, end_day, expiry=None):

	df = nsepy.get_history(symbol=ticker,
					   start=convert_date(start_day),
					   end=convert_date(end_day))

	return df

def get_futures_data(ticker,start_day,end_day,expiry):

	if ticker == 'NIFTY':
		# Stock options (Similarly for index options, set index = True)
		df = nsepy.get_history(symbol=ticker, start=convert_date(start_day),
						 end=convert_date(end_day), index=True,
						 expiry_date=convert_date(expiry))

	else:
		# Stock options (Similarly for index options, set index = True)
		df = nsepy.get_history(symbol=ticker,start=convert_date(start_day),
			 			 end=convert_date(end_day),futures=True,
			 			 expiry_date=convert_date(expiry))

	print "Getting data for %s : %s" %(ticker,expiry)
	return df


def main():
	parser = argparse.ArgumentParser(description='Pairs strategy for stocks')
	parser.add_argument('-y', '--YStock', help='NSE first stock symbol', required=False)
	parser.add_argument('-x', '--XStock', help='NSE second stock symbol', required=False)
	parser.add_argument('-d', '--delta', help='Start date', required=False, default=262)
	parser.add_argument('-f', '--future', help='Flag for stock futures', required=False, action='store_true', default=False)
	parser.add_argument('-I', '--nifty', help='Flag for NIFTY index', required=False, action='store_true', default=False)
	parser.add_argument('-B', '--bnifty', help='Flag for BANK NIFTY index', required=False, action='store_true', default=False)
	parser.add_argument('-U', '--US', help='Flag for US Futures', required=False, action='store_true',
						default=False)
	parser.add_argument('-A', '--niftyauto', help='Flag for Nifty Auto',required=False, action='store_true', default=False)
	parser.add_argument('-M', '--niftymetal', help='Flag for Nifty Metals', required=False, action='store_true', default=False)
	parser.add_argument('-IT', '--niftyit', help='Flag for Nifty IT', required=False, action='store_true', default=False)
	parser.add_argument('-index', help='Flag for Index', required=False, action='store_true', default=False)
	parser.add_argument('-del',help='Delete Flag', required=False, action='store_true', default=False)
	args = vars(parser.parse_args())

	# Initialize
	eTime = datetime.date.today()
	t_delta = datetime.timedelta(days=int(args['delta']))
	sTime = eTime - t_delta

    #Initialize Logging
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)

	# create a file handler
	_dir = constants.log_location+constants.timestr
	logname = _dir + '/'+constants.timestr+'.log'
	if not os.path.isdir(_dir):
		os.makedirs(_dir)
	#raise exception('Error in creating directory: %s' %(constants.log_location+constants.timestr))
	handler = logging.FileHandler(logname)
	handler.setLevel(logging.INFO)

	# create a logging format
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)

	# add the handlers to the logger
	logger.addHandler(handler)

	logger.info("Running Linear Regression")
	logger.info('Fetching Last %s days of data' % (args['delta']))

	if args['YStock']:
		if not args['future']:
			if not args['XStock']:
				print 'Please mention second stock'
				exit(0)
		else:
			print 'Fetching futures data for stock: %s' % (args['stockY'])

	##Check if NIFTY or BANKNIFTY or US Futures has been specified
	if args['nifty']:
		name = 'nifty'
		basket = constants.nifty50
	elif args['US']:
		name = 'INDICES'
		basket = constants.INDICES
	elif args['bnifty']:
		name = 'banknifty'
		basket = constants.banknifty
	elif args['niftyauto']:
		name = 'niftyauto'
		basket = constants.niftyauto
	elif args['niftymetal']:
		name = 'niftymetal'
		basket = constants.niftymetal
	elif args['niftyit']:
		name = 'niftyit'
		basket = constants.niftyit
	elif args['index']:
		name = 'index'
		basket = constants.index
	else:
		raise Exception('Specify correct argument')

	directory_name = constants.directory_name
	#Create directory if doesn't exist
	try:
		if not os.path.isdir(directory_name):
			os.makedirs(directory_name)
	except Exception,e:
		print e

	filename = '%s_%s.csv' % (name,constants.timestr)

	try:
		if args['del']:
			os.remove(directory_name + filename)
	except Exception,e:
		print e

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
		#if args['nifty'] or args['bnifty']:
		print sTime
		print eTime
		print t_delta
		if args['index']:
			data = pairTrader.pullindex(basket=basket, filename=directory_name+filename, sTime=sTime,
										eTime=eTime)
		else:
			data = pairTrader.pullData(stockY=args['YStock'],stockX=args['XStock'],
									future=args['future'], nifty=args['nifty'],
									bnifty=args['bnifty'],sTime=sTime,eTime=eTime,
									basket=basket, filename=directory_name+filename)
		#Condition for US Futures
		#else:
		#	data = pairTrader.usfutures(basket=basket, filename=directory_name+filename)

	if args['YStock'] and args['XStock']:
		pairTrader.model_current_std_err(data, YStock=args['YStock'], XStock=args['XStock'],search_string='lastPrice')
		pairTrader.model_current_std_err(data, YStock=args['YStock'], XStock=args['XStock'],search_string='open')

		exit(0)

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
	S1 = data['BANKNIFTY']
	S2 = data['RBLBANK']
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
