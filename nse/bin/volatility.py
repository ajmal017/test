import numpy as np
import pandas as pd
import pandas.io.data as web
import matplotlib.pyplot as plt
import os


stock = 'ONGC.NS'

window_size = pd.Timedelta('24D')/pd.Timedelta('1D')
print 'Window',window_size

T = 21

tick = web.DataReader(stock, data_source='yahoo',start='1/1/2016')

tick['LN_Ret'] = np.log(tick['Close'] / tick['Close'].shift(1))
tick['Volatility'] = pd.rolling_std(tick['LN_Ret'], window = T) * np.sqrt(T)
#tick[['Close', 'Volatility']].plot(subplots=True, color='blue',figsize=(10,8))

I = 200
z = np.random.standard_normal(I)
plt.hist(z, bins=50)
plt.show()