#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Abhishek v1.1
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
import platform
from statsmodels.tsa.stattools import coint
import logging
import utils

# Initialize the constants
_const = utils.constants()

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

	print("Getting data for %s : %s" %(ticker,expiry))
	return df


def initialize_logging(args):
	#Initialize Logging
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)

	# create a file handler
	_dir = _const.log_location+_const.timestr
	logname = _dir + '/'+_const.timestr+'.log'
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


	initialize_logging(args)

	# Initialize
	eTime = datetime.date.today()
	t_delta = datetime.timedelta(days=int(args['delta']))
	sTime = eTime - t_delta


	if args['YStock']:
		if not args['future']:
			if not args['XStock']:
				print('Please mention second stock')
				exit(0)
		else:
			print('Fetching futures data for stock: %s' % (args['stockY']))

	##Check if NIFTY or BANKNIFTY or US Futures has been specified

	if args['nifty']:
		name = 'nifty'
		basket = _const.nifty50
	elif args['US']:
		name = 'INDICES'
		basket = _const.INDICES
	elif args['bnifty']:
		name = 'banknifty'
		basket = _const.banknifty
	elif args['niftyauto']:
		name = 'niftyauto'
		basket = _const.niftyauto
	elif args['niftymetal']:
		name = 'niftymetal'
		basket = _const.niftymetal
	elif args['niftyit']:
		name = 'niftyit'
		basket = _const.niftyit
	elif args['index']:
		name = 'index'
		basket = _const.index
	else:
		raise Exception('Specify correct argument')

	directory_name = _const.directory_name
	#Create directory if doesn't exist
	try:
		if not os.path.isdir(directory_name):
			os.makedirs(directory_name)
	except Exception as e:
		print(e)

	filename = '%s_%s.csv' % (name,_const.timestr)

	try:
		if args['del']:
			os.remove(directory_name + filename)
	except Exception as e:
		print(e)

	_pull = pairTrader.pull(basket=basket, filename=directory_name+filename, sTime=sTime,
										eTime=eTime, constants=_const)

	if os.path.isfile(directory_name+filename):
		print('Data already downloaded in file: %s' %(directory_name+filename))
		try:
			data = pd.read_csv(directory_name+filename,comment='"')
			#Set Date as index
			data.set_index('Date', inplace=True)
			data.sort_values(by=['Date'],ascending=False)
		except Exception as e:
			print(e)
	else:
		print(sTime, eTime, t_delta)
		"""Pull data from history"""
		data = _pull.pullData()

	if args['YStock'] and args['XStock']:
		model = pairTrader.pairTrader(data, YStock=args['YStock'], XStock=args['XStock'])
		model.model_current_std_err(search_string='lastPrice')
		model.model_current_std_err(search_string='open')
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
	if not pairTrader.LinearRegression_MODEL(data=data, filename=filename):
		print('Unable to execute linear regression.')

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
