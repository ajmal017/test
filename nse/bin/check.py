import usfutures
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
columns = ['Date','CME_YM2','CME_CL18','CME_NQ2','CME_ES2', 'CME_GC2']
file='C:\\Users\\abhi\\Documents\projects\\test\data\usfutures\\20181005\MERGED.csv'
fobj = pd.read_csv(file, skiprows=1, index_col='Date', names=columns)
fobj.dropna()
print fobj.tail()

import pairTrader

n = fobj.shape[1]
keys = fobj.keys()

for i in range(n):
    for j in range(i+1, n):
        Y = np.asarray(fobj[keys[i]])
        X = np.asarray(fobj[keys[j]])

        model = pairTrader.linreg(Y=Y, X=X)
        inverse_model = pairTrader.linreg(Y=X, X=Y)
        if pairTrader.get_std_err_ratio(model) < pairTrader.get_std_err_ratio(inverse_model):
            # print '\tChoosing YStock : %s XStock: %s' % (keys[i],keys[j])
            chosen_model = model
        else:
            chosen_model = inverse_model

        #Y = np.asarray(fobj.CME_GC2)
        #X = np.asarray(fobj.CME_CL18)
        #model = pairTrader.linreg(Y=Y, X=X)
        #inverse = pairTrader.linreg(Y=X, X=Y)

        high = 1.0
        low = -1.0
        if chosen_model.f_pvalue < 0.02 and pairTrader.get_beta(chosen_model) > 0:
            cse = float(pairTrader.get_current_std_err(chosen_model))
            if (cse-high)*(cse-low) >= 0:
                print 'Y = %s, X =  %s' %(keys[i], keys[j])
                print 'Beta %4f' % float(pairTrader.get_beta(chosen_model))
                print 'STD_Err', pairTrader.get_current_std_err(chosen_model)
                print 'PValue: %.4f' %chosen_model.f_pvalue
                print 'Alpha %'

                plt.plot(X,Y,'r.')
                ax = plt.axis()
                x = np.linspace(ax[0], ax[1])
                plt.plot(x, chosen_model.params[0] + chosen_model.params[1] * x, 'b', lw=1)
                plt.grid(True)
                plt.axis('tight')
                plt.xlabel(keys[j])
                plt.ylabel(keys[i])
                #plt.show()
"""
plt.plot( Y,X, 'r.')
ax = plt.axis()
x = np.linspace(ax[0], ax[1])
plt.plot(x, model.params[0] + model.params[1] * x, 'b', lw=2)
plt.grid(True)
plt.axis('tight')
plt.xlabel('CME_CL18')
plt.ylabel('CME_NQ2')
plt.show()
"""