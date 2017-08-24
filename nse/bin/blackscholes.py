# python standard modules
import time
import datetime as dt
from math import sqrt, pi


# import numpy, pyplot and scipy
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# import pandas
import pandas as pd
# new in 0.17.1
from pandas_datareader import data as pd
plt.style.use('seaborn-darkgrid')
plotPath = "/Users/abhishek.chaturvedi/PycharmProjects/self/test/data/"
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy
from scipy.stats import norm
from scipy.optimize import brentq
from scipy.interpolate import interp1d

from options import *

# underlying stock price
S = 9427.9

# series of underlying stock prices to demonstrate a payoff profile
S_ = np.arange(9400.0, 9600.0, 0.05)
# strike price
K = 8700.0

# time to expiration (you'll see this as T-t in the equation)
t = 6.0/365.0

# risk free rate (there's nuance to this which we'll describe later)
r = 0.062735

# volatility (latent variable which is the topic of this talk)
vol = 0.1123

# use a lambda for a call payoff function
# equivelant to:
#
# def call_payoff(S, K):
#     return np.maximum(S - K, 0.0)
call_payoff = lambda S, K: np.maximum(S_ - K, 0.0)

# and put payoff function
put_payoff = lambda S, K: np.maximum(K - S_, 0.0)

# plot the call payoff
plt.figure(1)
plt.title('Call option payoff at expiration')
plt.xlabel('Underlying stock price, S')
plt.plot(S_, call_payoff(S_, K))

# plot the put payoff
plt.figure(2)
plt.title('Put option payoff at expiration')
plt.xlabel('Underlying stock price, S')
plt.plot(S_, put_payoff(S_, K))

print 'Black-Scholes call value %0.2f' % black_scholes_call_value(S, K, r, t, vol)
print 'Black-Scholes put value %0.2f' % black_scholes_put_value(S, K, r, t, vol)

# get the value of the option with six months to expiration
black_scholes_call_value_six_months = black_scholes_call_value(S_, K, r, 0.5, vol)

# get the value of the option with three months to expiration
black_scholes_call_value_three_months = black_scholes_call_value(S_, K, r, 0.25, vol)

# get the value of the option with one month to expiration
black_scholes_call_value_one_month = black_scholes_call_value(S_, K, r, 1.0/12.0, vol)

# get payoff value at expiration
call_payoff_at_expiration = call_payoff(S_, K)

# plot the call payoffs
plt.figure(3)
plt.plot(S_, black_scholes_call_value_six_months)
plt.plot(S_, black_scholes_call_value_three_months)
plt.plot(S_, black_scholes_call_value_one_month)
plt.plot(S_, call_payoff_at_expiration)
plt.title('Black-Schnoles price of option through time')
plt.xlabel('Underlying stock price, S')
plt.legend(['t=0.5', 't=0.25', 't=0.083', 't=0'], loc=2)
# print each of the results
print 'Black-Scholes call delta %0.4f' % call_delta(S, K, r, t, vol)
print 'Black-Scholes put delta %0.4f' % put_delta(S, K, r, t, vol)
print 'Black-Scholes gamma %0.4f' % gamma(S, K, r, t, vol)
print 'Black-Scholes vega %0.4f' % vega(S, K, r, t, vol)
print 'Black-Scholes call theta %0.4f' % call_theta(S, K, r, t, vol)
print 'Black-Scholes put theta %0.4f' % put_theta(S, K, r, t, vol)
print 'Black-Scholes call rho %0.4f' % call_rho(S, K, r, t, vol)
print 'Black-Scholes put rho %0.4f' % put_rho(S, K, r, t, vol)

# get the call and put values to test the implied volatility output
call_model_price = black_scholes_call_value(S, K, r, t, vol)
print 'Call implied volatility if market and model were equal (should be close to 0.25) %0.6f' % call_implied_volatility(S, K, r, t, call_model_price)

put_model_price = black_scholes_put_value(S, K, r, t, vol)
print 'Put implied volatility if market and model were equal (should be close to 0.25) %0.6f' % put_implied_volatility(S, K, r, t, put_model_price)


#plt.show()
