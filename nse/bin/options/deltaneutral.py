import numpy as np
from util import *
import mibian
import argparse
import datetime as dt
import matplotlib as mpl
#mpl.interactive(False)
import matplotlib.pyplot as plt
import pandas as pd
from option import round, option
# Constants
dir = "C:/Users/abhi/Documents/projects/test/nse/bin/options"
ir = 7.0
lotsize = 75
today = dt.datetime.now().date()
header = ['Spot','Expiry_strike','CE_intr_V','call_premium','CallPayoff','futureIV','FUTURE_Payoff','Payoff']
df_call_columns = ['OI','Chng in OI','Volume','IV','LTP','Net Chng',
'Bid Qty','Bid Price','Ask Price','Ask Qty','Strike_Price','delta','theta','vega','gamma']
df_put_columns = ['Strike_Price','Bid Qty','Bid Price','Ask Price','Ask Qty','Net Chng','LTP',
'IV','Volume','Chng in OI','OI','delta','theta','vega','gamma']

# Variables
spot = 11930.00
end = dt.date(2019, 6, 27)
call_sell_strike = 12200
put_sell_strike = 11400
future_buy_price = -11980
call_premium = 111.4
put_premium = 59.5
num_lots_calls = 2.0
num_lots_puts = 1.0
num_lots_futures = 1.0
put_iv = 17.7
call_iv = 10.14

dte = np.busday_count(today, end)
print("DTE: %s" % dte)

calldf = pd.read_csv(dir + '/call-test.csv',names=df_call_columns,na_values='-',delim_whitespace=True)
calldf.columns = calldf.columns.str.strip()
min_strike, max_strike, step = calldf['Strike_Price'].iloc[0], calldf['Strike_Price'].iloc[-1], 50
calldf = calldf.fillna(0)
calldf = calldf.dropna(subset=['IV','Ask Price','Bid Price'])
#print(calldf.head())

putdf = pd.read_csv(dir + '/put-test.csv',names=df_put_columns,na_values='-',delim_whitespace=True)
putdf.columns = putdf.columns.str.strip()
putdf = putdf.dropna(subset=['IV','Ask Price','Bid Price'])
putdf = putdf.fillna(0)
print(min_strike, max_strike)

def calculate_synthetic_straddle_payoff():
    df_ = pd.DataFrame({'Expiry_strike': range(min_strike, max_strike, step)})
    df_['Spot'] = np.repeat(spot, df_.__len__())
    df_['CE_intr_V'] = np.maximum(df_['Expiry_strike']-call_sell_strike, 0)
    df_['call_premium'] = np.repeat(call_premium, df_.__len__())
    df_['CallPayoff'] = num_lots_calls * (df_['call_premium'] - df_['CE_intr_V'])
    df_['futureIV'] = df_['Expiry_strike'] - future_buy_price
    df_['future_Payoff'] = df_['futureIV'] * num_lots_futures
    df_['Payoff'] = df_['future_Payoff'] + df_['CallPayoff']
    return df_

def calculate_strangle_payoff():
    df_ = pd.DataFrame({'Expiry_strike' : range(min_strike, max_strike, step)})
    df_ = pd.DataFrame()
    df_['Expiry_strike'] = calldf['Strike_Price']
    df_['Spot'] = np.repeat(spot, df_.__len__())
    df_['CE_intr_V'] = np.maximum(df_['Expiry_strike']-call_sell_strike, 0)
    df_['call_premium'] = np.repeat(call_premium, df_.__len__())
    df_['CallPayoff'] = num_lots_calls * (df_['call_premium'] - df_['CE_intr_V'])
    df_['PE_intr_V'] = np.maximum(put_sell_strike - df_['Expiry_strike'], 0)
    df_['put_premium'] = np.repeat(put_premium, df_.__len__())
    df_['put_Payoff'] = num_lots_puts * (df_['put_premium'] - df_['PE_intr_V'])
    df_['Payoff'] = df_['put_Payoff'] + df_['CallPayoff']
    return df_


def calculate_strangle_payoff_time():
    df_ = pd.DataFrame({'Expiry_strike' : range(min_strike, max_strike, step)})
    df_ = pd.DataFrame()
    df_['Expiry_strike'] = calldf['Strike_Price']
    df_['Spot'] = np.repeat(spot, df_.__len__())
    df_['CE_intr_V'] = np.maximum(df_['Expiry_strike']-call_sell_strike, 0)
    df_['call_premium'] = np.repeat(float(call_premium), df_.__len__())
    df_['CallPayoff'] = num_lots_calls * (df_['call_premium'] - df_['CE_intr_V'])
    df_['PE_intr_V'] = np.maximum(put_sell_strike - df_['Expiry_strike'], 0)
    df_['put_premium'] = np.repeat(put_premium, df_.__len__())
    df_['put_Payoff'] = num_lots_puts * (df_['put_premium'] - df_['PE_intr_V'])
    df_['Payoff'] = df_['put_Payoff'] + df_['CallPayoff']
    return df_


def plot_payoff(data, data_time,  x ,y):
    data.plot(x=x, y=y, color='blue', lw=1.5)
    data_time.plot(x=x, y=y, color='red', lw=1.5, style='-')
    plt.axvline(spot, lw=1.0, linestyle='--', label='Spot')
    plt.axhline(0, lw=1.0, linestyle='--', color='r')
    plt.grid(True)
    plt.xlim(spot-1000, spot+1000)
    plt.xlabel('Strike Prices')
    plt.ylabel('Payoff')
    plt.title('Strategy Payoff')
    plt.savefig(dir + '/strategy_payoff.png')


def main():
    parser = argparse.ArgumentParser(description='Strategy payoff calculator')
    parser.add_argument('-a', '--strangle', help='Strangle', required=False, action='store_false')
    parser.add_argument('-b', '--synthetic', help='Synthetic', required=False, action='store_false')
    args = vars(parser.parse_args())
    x = 'Expiry_strike'
    y = 'Payoff'

    """
    if args['synthetic']:
        data = calculate_synthetic_straddle_payoff()
        data.to_csv(dir + '/sythetic.csv')
        plot_payoff(data, x=x , y=y)
    if args['strangle']:
        data = calculate_strangle_payoff()
        data.to_csv(dir+'/strangle.csv')
        plot_payoff(data, data_time, x=x , y=y)
    """

    copt = mibian.BS([spot, call_sell_strike, ir, dte], volatility=call_iv)
    popt = mibian.BS([spot, put_sell_strike, ir, dte], volatility=put_iv)

    data = calculate_strangle_payoff()
    data_time = calculate_strangle_payoff_time()
    data.to_csv(dir + '/strangle.csv')
    plot_payoff(data, data_time, x=x, y=y)
    plt.show()
    print("\tStrike" + '\t' + "DELTA" + '\t' + "THETA" + '\t' + "VEGA")
    print("CALL:" +'\t'+round(call_sell_strike) + '\t' + round(copt.callDelta)
          + '\t' + round(copt.callTheta) + '\t' + round(copt.vega))
    print("PUT:" + '\t'+round(put_sell_strike) + '\t' + round(popt.putDelta)
          + '\t' + round(popt.putTheta) + '\t' + round(popt.vega))
    print("position delta:", 0 - num_lots_puts * popt.putDelta - num_lots_calls * copt.callDelta)
    print("position Vega:", lotsize * (num_lots_puts * popt.vega + num_lots_calls * copt.vega))
    print("position Theta:", lotsize * (num_lots_puts * popt.putTheta + num_lots_calls * copt.callTheta))


if __name__ == "__main__":
    # execute only if run as a script
    main()