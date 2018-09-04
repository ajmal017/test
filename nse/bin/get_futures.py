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
import statsmodels
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt
#variables
front_expiry = '2018,09,27'
back_expiry = '2018,10,25'
start_day = '2018,08,01'
end_day = '2018,08,31'
ticker = 'PNB'
timestr = time.strftime("%Y%m%d")
filename = 'data_%s.csv' % timestr
#location = "/Users/abhishek.chaturvedi/Documents/Work/Projects/test/data/"
location= "e:\\Python2.7\\projects\\test\\data\\"

banknifty = ['AXISBANK','BANKBARODA','HDFCBANK','ICICIBANK','IDFCBANK','INDUSINDBK','KOTAKBANK',
			 'PNB','RBLBANK','SBIN','YESBANK']
basket = ['PNB','SBIN','YESBANK']
nifty50 = ['ACC.NS','ADANIPORTS.NS','AMBUJACEM.NS','ASIANPAINT.NS','AXISBANK.NS','BAJAJ-AUTO.NS','BANKBARODA.NS',
'BHEL.NS','BPCL.NS','BHARTIARTL.NS','BOSCHLTD.NS','AUROPHARMA.NS','CIPLA.NS','COALINDIA.NS','DRREDDY.NS','GAIL.NS','GRASIM.NS',
'HCLTECH.NS','HDFCBANK.NS','HEROMOTOCO.NS','HINDALCO.NS','HINDUNILVR.NS','HDFC.NS','ITC.NS','ICICIBANK.NS','IDEA.NS','INDUSINDBK.NS','INFY.NS',
'KOTAKBANK.NS','LT.NS','LUPIN.NS','M&M.NS','MARUIT.NS','NTPC.NS','ONGC.NS','POWERGRID.NS','INFRATEL.NS','RELIANCE.NS','SBIN.NS',
'SUNPHARMA.NS','TCS.NS','TATAMOTORS.NS','TATAPOWER.NS','TATASTEEL.NS','TECHM.NS','ULTRATECH.NS','EICHERMOT.NS','WIPRO.NS','YESBANK.NS',
'ZEEL.NS','TATAMTRDVR.NS']

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

def create_file_from_df(fName,df):

	try:
		df.to_csv(location + '%s' % fName)
		
	except Exception,e:
		print e
	
	print 'Created file : %s' % fName
	return None

	
def find_cointegrated_pairs(data):
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            S1 = data[keys[i]]
            S2 = data[keys[j]]
            result = coint(S1, S2)
            score = result[0]
            pvalue = result[1]
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < 0.02:
                pairs.append((keys[i], keys[j]))
    return score_matrix, pvalue_matrix, pairs

def pullData(stockY=None,stockX=None, future=False, nifty=False, bnifty=False,sTime=None, eTime=None,basket=basket):

	merge = pd.DataFrame(columns=['Date'])
	first_stock = nsepy.get_history(symbol=basket[0], start=sTime, end=eTime)
	
	for i in range(1,len(basket)):
		dfstock = nsepy.get_history(symbol=basket[i], start=sTime, end=eTime)

		if i == 1:
			data = pd.concat([first_stock['Close'].rename(basket[0]),
							   dfstock['Close'].rename(basket[i])], 
						       axis=1)
		else:
			data = pd.concat([data, dfstock['Close'].rename(basket[i])], 
						       axis=1)
	
	#Set Date as index
	#data.set_index('Date', inplace=True)
	data.replace([np.inf,-np.inf], np.nan).dropna()
	data.sort_values(by=['Date'],ascending=False)
	create_file_from_df(fName=filename,df=data)
	
	return data
	
	
	
	if False:
		df_stockY = nsepy.get_history(symbol=stockY, start=sTime,end=eTime)
		df_stockX = nsepy.get_history(symbol=stockX, start=sTime,end=eTime)
		
		
		merge = pd.concat([df_stockY['Close'].rename(stockY),df_stockX['Close'].rename(stockX)], axis=1)
		print merge.head()
		#merge = pd.concat([df_stockY[['Open','Close']], df_stockX[['Open','Close']]], axis=1)
		#print 'Creating merged CSV files for stocks %s & %s' % ( stockY, stockX)
		#merge.to_csv(location + "merge_%s_%s.csv" % (stockY, stockX))
	if False:

		front_month = nsepy.get_futures_data(ticker, start_day, end_day, front_expiry)
		back_month =  nsepy.get_futures_data(ticker, start_day, end_day, back_expiry)
		columns = ['fO','fC','bO','bC']
		merge = pd.concat([front_month[['Open','Close']],back_month[['Open','Close']]],axis=1)

	#Create the merged CSV file
	#merge.to_csv(location+"merge_%s.csv" % ticker)


def main():
	parser = argparse.ArgumentParser(description='Pairs strategy for stocks')
	parser.add_argument('-s1', '--stockY', help='NSE first stock symbol', required=True)
	parser.add_argument('-s2', '--stockX', help='NSE second stock symbol', required=True)
	parser.add_argument('-d', '--delta', help='Start date', required=True)
	parser.add_argument('-f', '--future', help='Flag for stock futures', required=False, action='store_true', default=False)
	parser.add_argument('-I', '--nifty', help='Flag for NIFTY index', required=False, action='store_true', default=False)
	parser.add_argument('-B', '--bnifty', help='Flag for BANK NIFTY index', required=False, action='store_true', default=False)
	args = vars(parser.parse_args())

	# Initialize
	eTime = datetime.date.today()
	t_delta = datetime.timedelta(days=int(args['delta']))
	sTime = eTime - t_delta

	print('Fetching Last %s days of data' % (args['delta']))

	if args['stockY']:
		if not args['future']:
			if not args['stockX']:
				print 'Please mention second stock'
				exit(0)
		else:
			print 'Fetching futures data for stock: %s' % (args['stockY'])

	if os.path.isfile(location+filename):
		print 'Data already downloaded'
		try:
			data = pd.read_csv(location+filename)
			#Set Date as index
			data.set_index('Date', inplace=True)
			data.sort_values(by=['Date'],ascending=False)
		except Exception, e:
			print e
	else:
		data = pullData(stockY=args['stockY'],stockX=args['stockX'],
			 future=args['future'], nifty=args['nifty'], bnifty=args['bnifty'],sTime=sTime,eTime=eTime,
			 basket=banknifty)
		
		
	# Heatmap to show the p-values of the cointegration test
	# between each pair of stocks
	scores, pvalues, pairs = find_cointegrated_pairs(data)

	m = [0,0.2,0.4,0.6,0.8,1]
	seaborn.heatmap(pvalues, xticklabels=banknifty, yticklabels=banknifty,
		cmap='RdYlGn_r',
		mask = (pvalues >= 0.98))
	plt.show()
	print 'Possible trade in the followig pairs:\n',pairs
	
			 
if __name__ == '__main__':
	main()