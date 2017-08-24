import numpy as np
import pandas as pd
import pandas.io.data as web
import matplotlib.pyplot as plt
from sklearn.decomposition import KernelPCA

symbols = ['ACC.NS','ADANIPORTS.NS','AMBUJACEM.NS','ASIANPAINT.NS','AXISBANK.NS','BAJAJ-AUTO.NS','BANKBARODA.NS',
'BHEL.NS','BPCL.NS','BHARTIARTL.NS','BOSCHLTD.NS','AUROPHARMA.NS','CIPLA.NS','COALINDIA.NS','DRREDDY.NS','GAIL.NS','GRASIM.NS',
'HCLTECH.NS','HDFCBANK.NS','HEROMOTOCO.NS','HINDALCO.NS','HINDUNILVR.NS','HDFC.NS','ITC.NS','ICICIBANK.NS','IDEA.NS','INDUSINDBK.NS','INFY.NS',
'KOTAKBANK.NS','LT.NS','LUPIN.NS','M&M.NS','MARUIT.NS','NTPC.NS','ONGC.NS','POWERGRID.NS','INFRATEL.NS','RELIANCE.NS','SBIN.NS',
'SUNPHARMA.NS','TCS.NS','TATAMOTORS.NS','TATAPOWER.NS','TATASTEEL.NS','TECHM.NS','ULTRATECH.NS','EICHERMOT.NS','WIPRO.NS','YESBANK.NS',
'ZEEL.NS','TATAMTRDVR.NS']

#symbols = ['ONGC.NS','SBIN.NS','PNB.NS','^NSEI']
data = pd.DataFrame()
for eachsym in symbols:
	#Download the Closing Prices
	data[eachsym] = web.DataReader(eachsym, data_source='yahoo')['Close']
data = data.dropna()

nifty50 = pd.DataFrame(data.pop('^NSEI'))
scale_function = lambda x: (x - x.mean()) / x.std()
pca = KernelPCA(n_components=5).fit(data.apply(scale_function))
nifty50['PCA_1'] = pca.transform(-data)

nifty50.apply(scale_function).plot(figsize=(10,6))
plt.show()
