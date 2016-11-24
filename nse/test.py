import datetime
import argparse
from datetime import date

parser = argparse.ArgumentParser(description='STOCK volatility calculator')
#parser.add_argument('-s', '--stock', help='NSE stock symbol', required=True)
parser.add_argument('-d','--delta', help='Start date', required=True)
args = vars(parser.parse_args())

today = datetime.date.today()
delta = datetime.timedelta(days=int(args['delta']))

yesterday = today - delta

print today
print yesterday

print 'Year:', today.year
print 'Mon :', today.month
print 'Day :', today.day

print

print(date(today.year,today.month, today.day))
