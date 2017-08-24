import numpy as np
import pandas as pd
import os, sys
import argparse

parser = argparse.ArgumentParser(description='Future spread calculator')
parser.add_argument('-d', '--dte', help='NSE stock symbol', required=True)
parser.add_argument('-s', '--price', help='NSE stock symbol', required=True)

args = vars(parser.parse_args())

current_price = float(args['price'])
rrate = 6.1495
fair_price = current_price * (1+rrate/100*(float(args['dte'])/365))

print 'Fair Price: ',round(fair_price,2)

