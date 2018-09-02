#Abhishek v1.0
# Date : Aug/31/2018
# To get NIFTY individual stocks futures converted to dataframes
import nsepy
from datetime import date, datetime
import pandas as pd
import argparse
import datetime

#variables
front_expiry = '2018,09,27'
back_expiry = '2018,10,25'
start_day = '2018,08,01'
end_day = '2018,08,31'
ticker = 'PNB'
location = "/Users/abhishek.chaturvedi/Documents/Work/Projects/test/data/"

banknifty = ['AXISBANK','BANKBARODA','FEDERALBANK','HDFCBANK','ICICIBANK','IDFCBANK','INDUSINDBK','KOTAKBANK',
			 'PNB','RBLBANK','SBIN','YESBANK']
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

def pullData(stockY=None,stockX=None, delta=None, future=False, nifty=False, bnifty=False,sTime=None, eTime=None):

	if not future:
		df_stockY = nsepy.get_history(symbol=stockY, start=sTime,end=eTime)
		df_stockX = nsepy.get_history(symbol=stockX, start=sTime,end=eTime)

		merge = pd.concat([df_stockY[['Open','Close']], df_stockX[['Open','Close']]], axis=1)
		print 'Creating merged CSV files for stocks %s & %s' % ( stockY, stockX)
		merge.to_csv(location + "merge_%s_%s.csv" % (stockY, stockX))
	else:

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

	print('Fetching Last %s days of data for stocks: %s & %s' % (args['delta'], args['stockY'], args['stockX']))

	if args['stockY']:
		if not args['future']:
			if not args['stockX']:
				print 'Please mention second stock'
				exit(0)
		else:
			print 'Fetching futures data for stock: %s' % (args['stockY'])

	pullData(stockY=args['stockY'],stockX=args['stockX'],delta=args['delta'],
			 future=args['future'], nifty=args['nifty'], bnifty=args['bnifty'],sTime=sTime,eTime=eTime)

if __name__ == '__main__':
	main()