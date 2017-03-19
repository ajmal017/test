import pandas as pd
import pandas.io.data as web

symbols = ['^GDAXI','^GSPC','YHOO','MSFT']
data= pd.Dataframe()
for sym in symbols:
    data[sym] = web.DataReader(sym, data_source='yahoo'
                               ,start ='1/1/2016')['Adj Close']
data =  data.dropna()
print data.info()
