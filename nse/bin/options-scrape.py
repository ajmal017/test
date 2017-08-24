import os, sys
import pandas
from pandas_datareader import data as pd
from utils import *



# define a stock symbol
underlying_symbol = 'CRM'

if not os.path.isfile('%s.p' % underlying_symbol):
    # define a Options object
    options_obj = pd.Options(underlying_symbol, 'yahoo')
    # request all chains for the underlying symbol
    # ***WARNING THIS TAKES A WHILE***
    options_frame_live = options_obj.get_all_data()
    # let's pickle the dataframe so we don't have to hit the network every time
    options_frame_live.to_pickle('%s.p' % underlying_symbol)


# read the original frame in from cache (pickle)
options_frame = pandas.read_pickle('%s.p' % underlying_symbol)
# and the first ten records
#print options_frame_live.head()
# reset the index so the strike and expiration become columns
options_frame.reset_index(inplace=True)
# remove PctChg and IV - we'll calculate our own
del options_frame['PctChg']
del options_frame['IV']
# rename the columns for consistency
columns = {'Expiry': 'Expiration',
           'Type': 'OptionType',
           'Symbol': 'OptionSymbol',
           'Vol': 'Volume',
           'Open_Int': 'OpenInterest',
           'Underlying_Price': 'UnderlyingPrice',
           'Quote_Time': 'QuoteDatetime',
           'Underlying': 'UnderlyingSymbol',
           'Chg': 'OptionChange'}

options_frame.rename(columns=columns, inplace=True)

# use the apply method to pass each row as a series to the various methods, returns a series in this case
options_frame['DaysUntilExpiration'] = options_frame.apply(get_days_until_expiration, axis=1)
options_frame['TimeUntilExpiration'] = options_frame.apply(get_time_fraction_until_expiration, axis=1)
options_frame['InterestRate'] = options_frame.apply(get_rate, axis=1)
options_frame['Mid'] = options_frame.apply(get_mid, axis=1)

# apply the function to the dataframe rowwise
options_frame['ImpliedVolatilityMid'] = options_frame.apply(get_implied_vol_mid, axis=1)
bad_iv = options_frame[np.isnan(options_frame['ImpliedVolatilityMid'])]
# map the count function to each strike where there is a nan implied volatility
bad_iv.groupby(['Strike']).count()['Expiration']

# get the completed frame
options_frame = interp_implied_volatility(options_frame)
# check to see if there are any np.nans
bad_iv_post = options_frame[np.isnan(options_frame['ImpliedVolatilityMid'])]
print bad_iv_post.groupby(['Strike']).count()['Expiration']
print options_frame.head()

# use the apply method to pass each row as a series to the various methods, returns a series in this case
options_frame['TheoreticalValue'] = options_frame.apply(get_option_value, axis=1)
options_frame['Delta'] = options_frame.apply(get_delta, axis=1)
options_frame['Gamma'] = options_frame.apply(get_gamma, axis=1)
options_frame['Vega'] = options_frame.apply(get_vega, axis=1)
options_frame['Theta'] = options_frame.apply(get_theta, axis=1)
options_frame['Rho'] = options_frame.apply(get_rho, axis=1)
options_frame['ModelError'] = options_frame.apply(get_model_error, axis=1)

# plot the model error
options_frame['ModelError'].hist()
# grab the index of the 50 largest abs(errors)
sorted_errors_idx = options_frame['ModelError'].map(abs).sort_values(ascending=False).head(50)

# get the rest of the details from the frame
errors_20_largest_by_strike = options_frame.ix[sorted_errors_idx.index]

# plot model error against strike
errors_20_largest_by_strike[['Strike', 'ModelError']].sort_values(by='Strike').plot(kind='bar', x='Strike')
# add a new column
options_frame['BidAskSpread'] = options_frame['Ask'] - options_frame['Bid']

# plot model error by bid-ask spread
errors_20_largest_by_spread = options_frame.ix[sorted_errors_idx.index]

# plot model error against strike, many expirations included
errors_20_largest_by_spread[['BidAskSpread', 'ModelError']].sort_values(by='BidAskSpread').plot(kind='bar', x='BidAskSpread')
# plot a scatter plot of all errors > 1.0e-4
options_frame[abs(options_frame['ModelError']) >= 1.0e-4].plot(kind='scatter', x='BidAskSpread', y='ModelError')

# select an expiration to plot
iv = options_frame[options_frame['Expiration'] == '2017-05-26']

# get the call options
iv_call = iv[iv['OptionType'] == 'call']

# set the strike as the index so pandas plots nicely
iv_call[['Strike', 'ImpliedVolatilityMid']].set_index('Strike').plot(title='Implied volatility skew')

# get the monthly expirations
expirations = options_frame['Expiration'].unique()[-5:]

# get all the rows where expiration is in our list of expirations
iv_multi = options_frame[options_frame['Expiration'].isin(expirations)]

# get the call options
iv_multi_call = iv_multi[iv_multi['OptionType'] == 'call']

# pivot the data frame to put expiration dates as columns
iv_pivoted = iv_multi_call[['DaysUntilExpiration', 'Strike', 'ImpliedVolatilityMid']].pivot(index='Strike', columns='DaysUntilExpiration', values='ImpliedVolatilityMid').dropna()

# plot
iv_pivoted.plot()

# select a strike to plot
iv = options_frame[options_frame['Strike'] == 100.0]

# get the call options
iv_call = iv[iv['OptionType'] == 'call']

# set the strike as the index so pandas plots nicely
iv_call[['Expiration', 'ImpliedVolatilityMid']].set_index('Expiration').plot()

# pivot the dataframe
iv_pivoted_surface = iv_multi_call[['DaysUntilExpiration', 'Strike', 'ImpliedVolatilityMid']].pivot(index='Strike', columns='DaysUntilExpiration', values='ImpliedVolatilityMid').dropna()

# create the figure object
fig = plt.figure()

# add the subplot with projection argument
ax = fig.add_subplot(111, projection='3d')

# get the 1d values from the pivoted dataframe
x, y, z = iv_pivoted_surface.columns.values, iv_pivoted_surface.index.values, iv_pivoted_surface.values

# return coordinate matrices from coordinate vectors
X, Y = np.meshgrid(x, y)

# set labels
ax.set_xlabel('Days to expiration')
ax.set_ylabel('Strike price')
ax.set_zlabel('Implied volatility')
ax.set_title('Implied volatility surface')

# plot
ax.plot_surface(X, Y, z, rstride=4, cstride=4, color='b')

plt.show()