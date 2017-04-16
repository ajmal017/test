import pandas as pd
from math import log, sqrt, exp
from scipy import stats
import pandas.io.data as web

def bsm_call_value(S0, K, T, r, sigma):
    # Valuation of European call option in BSM model

    S0 = float(S0)
    d1 = (log(S0 / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = (log(S0 / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    value = (S0 * stats.norm.cdf(d1, 0.0, 1.0)
            - K * exp(-r * T) * stats.norm.cdf(d2, 0.0, 1.0))

    return value

# Vega function
def bsm_vega(S0, K, T, r, sigma):
    # Vega of European option in BSM model

    S0 = float(S0)
    d1 = (log(S0 / K) + (r + 0.5 * sigma ** 2) * T / (sigma * sqrt(T)))
    vega = S0 * stats.norm.cdf(d1, 0.0, 1.0) * sqrt(T)
    return vega

# Implied volatility function
def bms_call_imp_vol(S0, K, T, r, C0, sigma_est, it=100):
    """ Implied volatility of European call option in BSM model.
    sigma_est : float estimate of implied volatility
    r : float constant risk free short rate
    T : maturity date ( in year fractions)
    K : strike price
    S0 : initial stock / index level
    """
    for i in range(it):
        sigma_est -= ((bsm_call_value(S0, K, T,r,sigma_est) - C0) / bsm_vega(S0, K, T,r, sigma_est))
    return sigma_est

V0 = 17.6639
r = 0.01 # 1%

path = '/Users/abhishek.chaturvedi/PycharmProjects/self/test/nse/'
filename = path + 'stock.h5'
h5 = pd.HDFStore(filename, 'r')
