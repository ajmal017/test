import numpy as np
from scipy.stats import norm

#### make a funcion that lets you specify a few parameters and calculates the payoff

# S = stock underlying
# K = strike price
# Price = premium paid for option
def long_call(S, K, Price):
    # Long Call Payoff = max(Stock Price - Strike Price, 0)
    # If we are long a call, we would only elect to call if the current stock price is greater than
    # the strike price on our option

    P = list(map(lambda x: max(x - K, 0) - Price, S))
    return P


def long_put(S, K, Price):
    # Long Put Payoff = max(Strike Price - Stock Price, 0)
    # If we are long a call, we would only elect to call if the current stock price is less than
    # the strike price on our option

    P = list(map(lambda x: max(K - x, 0) - Price, S))
    return P


def short_call(S, K, Price):
    # Payoff a shortcall is just the inverse of the payoff of a long call

    P = long_call(S, K, Price)
    return [-1.0 * p for p in P]


def short_put(S, K, Price):
    # Payoff a short put is just the inverse of the payoff of a long put

    P = long_put(S, K, Price)
    return [-1.0 * p for p in P]


def binary_call(S, K, Price):
    # Payoff of a binary call is either:
    # 1. Strike if current price > strike
    # 2. 0

    P = list(map(lambda x: K - Price if x > K else 0 - Price, S))
    return P


def binary_put(S, K, Price):
    # Payoff of a binary call is either:
    # 1. Strike if current price < strike
    # 2. 0

    P = list(map(lambda x: K - Price if x < K else 0 - Price, S))
    return P


def bull_spread(S, E1, E2, Price1, Price2):
    P_1 = long_call(S, E1, Price1)
    P_2 = short_call(S, E2, Price2)
    return [x + y for x, y in zip(P_1, P_2)]


def bear_spread(S, E1, E2, Price1, Price2):
    P = bull_spread(S, E1, E2, Price1, Price2)
    return [-1.0 * p + 1.0 for p in P]


def straddle(S, E, Price1, Price2):
    P_1 = long_call(S, E, Price1)
    P_2 = long_put(S, E, Price2)
    return [x + y for x, y in zip(P_1, P_2)]


def risk_reversal(S, E1, E2, Price1, Price2):
    P_1 = long_call(S, E1, Price1)
    P_2 = short_put(S, E2, Price2)
    return [x + y for x, y in zip(P_1, P_2)]


def strangle(S, E1, E2, Price1, Price2):
    P_1 = long_call(S, E1, Price1)
    P_2 = long_put(S, E2, Price2)
    return [x + y for x, y in zip(P_1, P_2)]

def short_strangle(S, call_strike, put_strike, call_price, put_price):
    P_1 = short_call(S, call_strike, call_price)
    P_2 = short_put(S, put_strike, put_price)
    return [x + y for x, y in zip(P_1, P_2)]


def butterfly_spread(S, E1, E2, E3, Price1, Price2, Price3):
    P_1 = long_call(S, E1, Price1)
    P_2 = long_call(S, E3, Price3)
    P_3 = short_call(S, E2, Price2)
    P_3 = [2 * p for p in P_3]
    return [x + y + z for x, y, z in zip(P_1, P_2, P_3)]


def strip(S, E1, Price1, Price2):
    P_1 = long_call(S, E1, Price1)
    P_2 = long_put(S, E1, Price2)
    P_2 = [2 * p for p in P_2]
    return [x + y for x, y in zip(P_1, P_2)]


from scipy.stats import norm


# S: underlying stock price
# K: Option strike price
# r: risk free rate
# D: dividend value
# vol: Volatility
# T: time to expiry (assumed that we're measuring from t=0 to T)

def d1_calc(S, K, r, vol, T, t):
    # Calculates d1 in the BSM equation
    return (np.log(S / K) + (r + 0.5 * vol ** 2) * (T - t)) / (vol * np.sqrt(T - t))


def BS_call(S, K, r, vol, T, t):
    d1 = d1_calc(S, K, r, vol, T, t)
    d2 = d1 - vol * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def BS_put(S, K, r, vol, T, t):
    return BS_call(S, K, r, vol, T, t) - S + np.exp(-r * (T - t)) * K


def BS_binary_call(S, K, r, vol, T, t):
    d1 = d1_calc(S, K, r, vol, T, t)
    d2 = d1 - vol * np.sqrt(T - t)
    return np.exp(-r * T) * norm.cdf(d2)


def BS_binary_put(S, K, r, vol, T, t):
    return BS_binary_call(S, K, r, vol, T, t) - S + np.exp(-r * (T - t)) * K


###########################################################################
# 1st Order Greeks
def delta(S, K, r, vol, T, t, otype):
    d1 = d1_calc(S, K, r, vol, T, t)
    d2 = d1 - vol * np.sqrt(T - t)

    if (otype == "call"):
        delta = np.exp(-(T - t)) * norm.cdf(d1)
    elif (otype == "put"):
        delta = -np.exp(-(T - t)) * norm.cdf(-d1)

    return delta


# Gamma for calls/puts the same

def vega(S, K, r, vol, T, t, otype):
    d1 = d1_calc(S, K, r, vol, T, t)
    return S * norm.pdf(d1) * np.sqrt(T - t)


def rho(S, K, r, vol, T, t, otype):
    d1 = d1_calc(S, K, r, vol, T, t)
    d2 = d1 - vol * np.sqrt(T - t)

    if (otype == "call"):
        rho = K * (T - t) * np.exp(-r * (T - t)) * norm.cdf(d2)
    elif (otype == "put"):
        rho = -K * (T - t) * np.exp(-r * (T - t)) * norm.cdf(-d2)
    return rho


def theta(S, K, r, vol, T, t, otype):
    d1 = d1_calc(S, K, r, vol, T, t)
    d2 = d1 - vol * np.sqrt(T - t)

    if (otype == "call"):
        theta = -(S * norm.pdf(d1) * vol / (2 * np.sqrt(T - t))) - r * K * np.exp(-r * (T - t)) * norm.cdf(d2)
    elif (otype == "put"):
        theta = -(S * norm.pdf(d1) * vol / (2 * np.sqrt(T - t))) + r * K * np.exp(-r * (T - t)) * norm.cdf(-d2)

    return theta


# 2nd Order Greeks
def gamma(S, K, r, vol, T, t, otype):
    d1 = d1_calc(S, K, r, vol, T, t)
    gamma = (norm.pdf(d1)) / (S * vol * np.sqrt(T - t))

    return gamma


def charm(S, K, r, vol, T, t, otype):
    d1 = d1_calc(S, K, r, vol, T, t)
    d2 = d1 - vol * np.sqrt(T - t)
    charm = -norm.pdf(d1) * (2 * r * (T - t) - d2 * vol * np.sqrt(T - t)) / (2 * (T - t) * vol * np.sqrt(T - t))

    return charm