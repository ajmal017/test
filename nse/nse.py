from nsepy import get_history, get_index_pe_history
from datetime import date
"""
    get_history argument list
            symbol (str): Symbol for stock (SBIN, RELIANCE etc.), index (NIFTY, BANKNIFTY etc) or any security (Index names "NIFTY 50", "INDIAVIX" etc.
            start (datetime.date): start date
            end (datetime.date): end date
            index (boolean): False by default, True if its an index, index futures or options and also for INDIAVIX
            futures (boolean): False by default, True for index and stock futures only (should not be set to True with option_type specified)
            expiry_date (datetime.date): Expiry date for derivatives, Compulsory parameter for futures and options
            option_type (str): It takes "CE", "PE", "CA", "PA" for European and American calls and puts
            strike_price (int): Strike price, Compulsory parameter for options
            series (str): Defaults to "EQ", but can be "BE" etc (refer NSE website for details)
"""

#Stock history
sbin = get_history(symbol='SBIN',
                    start=date(2016,1,1),
                    end=date(2015,11,18))
sbin[[ 'VWAP', 'Turnover']].plot(secondary_y='Turnover')

""" Index price history
    symbol can take these values (These indexes have derivatives as well)
    "NIFTY" or "NIFTY 50",
    "BANKNIFTY" or "NIFTY BANK",
    "NIFTYINFRA" or "NIFTY INFRA",
    "NIFTYIT" or "NIFTY IT",
    "NIFTYMID50" or "NIFTY MIDCAP 50",
    "NIFTYPSE" or "NIFTY PSE"
    In addition to these there are many indices
    For full list refer- http://www.nseindia.com/products/content/equities/indices/historical_index_data.htm
"""
nifty = get_history(symbol="NIFTY",
                    start=date(2015,1,1),
                    end=date(2015,1,10),
                    index=True)
nifty[['Close', 'Turnover']].plot(secondary_y='Turnover')

#Futures and Options historical data
nifty_fut = get_history(symbol="NIFTY",
                        start=date(2015,1,1),
                        end=date(2015,1,10),
                        index=True,
                        futures=True, expiry_date=date(2015,1,29))

stock_opt = get_history(symbol="SBIN",
                        start=date(2015,1,1),
                        end=date(2015,1,10),
                        option_type="CE",
                        strike_price=300,
                        expiry_date=date(2015,1,29))

#Index P/E ratio history
nifty_pe = get_index_pe_history(symbol="NIFTY",
                                start=date(2015,1,1),
                                end=date(2015,1,10))
