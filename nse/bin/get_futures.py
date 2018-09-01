#Abhishek v1.0
# Date : Aug/31/2018
# To get NIFTY individual stocks futures converted to dataframes
from nsepy import get_history, get_index_pe_history
from datetime import date, datetime

#variables
front_expiry = '2018,09,27'
back_expiry = '2018,10,25'
start_day = '2018,08,20'
end_day = '2018,08,31'
ticker = 'SBIN'

def convert_date(stringO):

	convertedDate = datetime.strptime(stringO, "%Y,%m,%d").date()

	return convertedDate

def get_futures_data(ticker,start_day,end_day,expiry):

	# Stock options (Similarly for index options, set index = True)
	df = get_history(symbol=ticker,start=convert_date(start_day),
		 end=convert_date(end_day),futures=True,
		 expiry_date=convert_date(expiry))
	
	print "Getting data for %s : %s" %(ticker,expiry)
	return df
	
front_month = get_futures_data(ticker, start_day, end_day, front_expiry)

back_month = get_futures_data(ticker, start_day, end_day, back_expiry)

master_df = front_month['Open']
