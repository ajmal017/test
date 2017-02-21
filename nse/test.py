from mpl_toolkits.mplot3d import Axes3D
import matplotlib.finance as mpf
import matplotlib.pyplot as plt
import numpy as np
import pandas.io.data as web
import math
import pandas as pd

start=(2016,12,1)
end = (2017,2,1)

DAX = web.DataReader(name='GOOG',data_source='google',start=start)
#DAX['Close'].plot(figsize=(10,5))

DAX['Return'] = np.log(DAX['Close'] / DAX['Close'].shift(1))
#DAX[['Return']].plot(figsize=(8,5))
DAX['Mov_Vol'] = pd.rolling_std(DAX['Return'], window=252) * math.sqrt(252)
DAX[['Close','Mov_Vol','Return']].plot(subplots=True, style='b',figsize=(8,7))

plt.show()
