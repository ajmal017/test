#https://clinthoward.github.io/portfolio/2017/04/16/BlackScholesGreeks/
from util import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#plt.style.use('ggplot')
fig, ax = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True, figsize=(30, 25))
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['figure.titlesize'] = 18
plt.rcParams['figure.titleweight'] = 'medium'
plt.rcParams['lines.linewidth'] = 2.5

S = [t / 5 for t in range(8000, 15000)]  # Define some series of stock-prices

#sc_ss = short_strangle(S, call_strike=11550, put_strike=12000, call_price=35, put_price=21.5)
sc_ss = strangle(S, 11550, 12000,35, 21.5)
plt.plot(S, sc_ss, 'g')
plt.legend(["Short Strangle"])

plt.show()
