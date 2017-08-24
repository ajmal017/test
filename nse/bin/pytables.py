import numpy as np
import pandas as pd
import datetime as dt
#import matplotlib.pyplot as plt
import pandas.io.data as web

path = '/Users/abhishek.chaturvedi/PycharmProjects/self/test/nse/'
filename = path + 'stock.h5'
h5s = pd.HDFStore(filename, 'w')
stock = web.DataReader(name='^NSEI', data_source = 'yahoo',
						start = '2017-01-01')

h5s['stock'] = stock
h5s.close()

#print stock.tail()
#stock['Adj Close'].plot(figsize=(8,5))
#plt.show()

h5r = pd.HDFStore(filename,'r')
temp_read = h5r['stock']
print temp_read[:5]
h5r.close()
"""
#CSV method
filename = path + 'stock.csv'
csv_file = open(filename, 'w')
stock.to_csv(filename, sep=',', encoding='utf-8')

csv_file = open(filename, 'r')
content = csv_file.readlines()
for line in content[:5]:
    print line,
"""