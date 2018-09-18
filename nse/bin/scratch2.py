import numpy as np
import quandl
import pairTrader
import pandas as pd
import os
import termcolor
import datetime
import argparse
import time

class const:
    year= 2018
    #holidays = [dt(year,1,1),dt(year,1,15),dt(year,2,19),
    #            dt(year,3,30),dt(year,5,28),dt(year,7,3),dt(year,7,4),
    #            dt(year,9,3),dt(year,11,22),dt(year,11,23),dt(year,12,24),dt(year,12,25)]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    location = script_dir + '/../../data/'
    directory = script_dir + '/../../data/usfutures/'
    #directory = 'C:\\Users\\abhi\\Documents\\projects\\test\\data\\usfutures\\'

    futures = ['CME_YM2','CME_CL18','CME_NQ2','CME_ES2', 'CME_GC2']
    months = ['q','u','v','x','z']
    CL = ['clq%s' %year, 'clu%s' %year, 'clv%s' %year, 'clx%s' %year, 'clz%s' %year]
    GC = ['gcq%s' %year, 'gcu%s' %year, 'gcv%s' %year, 'gcx%s' %year, 'gcz%s' %year]
    QM = ['qmq%s' %year, 'qmu%s' %year, 'qmv%s' %year, 'qmx%s' %year, 'qmz%s' %year]
    NG = ['ngq%s' %year, 'ngu%s' %year, 'ngv%s' %year, 'ngx%s' %year, 'ngz%s' %year]
    QG = ['qgq%s' %year, 'qgu%s' %year, 'qgv%s' %year, 'qgx%s' %year, 'qgz%s' %year]
    # Create the dictionary of expiry dates for each contract
    #expiry_dates = pd.Series({'CLV2018': datetime.datetime(2018, 9, 15),
    #                          'CLX2018': datetime.datetime(2018, 10, 15)})

    expiry_dates = [datetime.datetime(year, 7,15), datetime.datetime(year, 8, 15), datetime.datetime(year, 9,15),
                    datetime.datetime(year, 10, 15), datetime.datetime(year, 11,15)]
    #Holidays
    #holidays = [dt(2018,1,1),dt(2018,1,15),dt(2018,2,19),
    #dt(2018,3,30),dt(2018,5,28),dt(2018,7,3),dt(2018,7,4),
    #dt(2018,9,3),dt(2018,11,22),dt(2018,11,23),dt(2018,12,24),dt(2018,12,25)]
    timestr = time.strftime("%Y%m%d")
    filename_for_merge_futures = 'merged_all_futures'


def futures_rollover_weights(start_date, expiry_dates, contracts, rollover_days=5):
    """This constructs a pandas DataFrame that contains weights (between 0.0 and 1.0)
    of contract positions to hold in order to carry out a rollover of rollover_days
    prior to the expiration of the earliest contract. The matrix can then be
    'multiplied' with another DataFrame containing the settle prices of each
    contract in order to produce a continuous time series futures contract."""

    # Construct a sequence of dates beginning from the earliest contract start
    # date to the end date of the final contract
    dates = pd.date_range(start_date, expiry_dates[-1], freq='B')

    # Create the 'roll weights' DataFrame that will store the multipliers for
    # each contract (between 0.0 and 1.0)
    roll_weights = pd.DataFrame(np.zeros((len(dates), len(contracts))),
                                index=dates, columns=contracts)
    prev_date = roll_weights.index[0]

    # Loop through each contract and create the specific weightings for
    # each contract depending upon the settlement date and rollover_days
    for i, (item, ex_date) in enumerate(expiry_dates.iteritems()):
        if i < len(expiry_dates) - 1:
            roll_weights.ix[prev_date:ex_date - pd.offsets.BDay(), item] = 1
            roll_rng = pd.date_range(end=ex_date - pd.offsets.BDay(),
                                     periods=rollover_days + 1, freq='B')

            # Create a sequence of roll weights (i.e. [0.0,0.2,...,0.8,1.0]
            # and use these to adjust the weightings of each future
            decay_weights = np.linspace(0, 1, rollover_days + 1)
            roll_weights.ix[roll_rng, item] = 1 - decay_weights
            roll_weights.ix[roll_rng, expiry_dates.index[i+1]] = decay_weights
        else:
            roll_weights.ix[prev_date:, item] = 1
        prev_date = ex_date
    return roll_weights

def pulldata(delta):
    # Initialize
    eTime = datetime.date.today()
    t_delta = datetime.timedelta(days=int(delta))
    sTime = eTime - t_delta

    columns = ['Date','Settle']
    running_df = pd.DataFrame(columns=columns)
    _dict = {}
    expiry_series = pd.Series

    first_contract = quandl.get("CHRIS/%s" % const.futures[0],authtoken="3v1zXUSUxysjyohgAQ3e",start_date=sTime, end_date=eTime)
    first_contract.name = const.futures[0]
    for i in range(1,len(const.futures)):
        # Scratch Variable
        list_of_df = []
        print 'Futures:', const.futures[i]
        contract_name = const.futures[i]
        print 'Downloading: %s' % contract_name
        data = quandl.get("CHRIS/%s" % contract_name, authtoken="3v1zXUSUxysjyohgAQ3e",start_date=sTime, end_date=eTime)
        data.name = contract_name
        list_of_df.append(data)
        tocsv(data)

        if i == 1:
            running_df = pd.concat([list_of_df[0].Settle.rename(const.futures[0]),
                                    data.Settle.rename(contract_name)], axis=1)
        else:
            running_df = pd.concat([running_df, data.Settle.rename(contract_name)], axis=1)

    # Output the merged series of contract settle prices
    tocsv(data=running_df, name='MERGED')
    return running_df


def merge_basket_frames(basket):
    ## Convert the basket stocks individual frames to a single dataframe in
    ## format: <date.index Stock1 Stock2 Stock3>
    ##          data       'price' 'price' 'price'
    comment = 'D'
    timestr = time.strftime("%m-%d-%Y")
    columns = ['Date','Settle']
    data = pd.DataFrame(columns=columns)
    for k,v in enumerate(const.futures):
        name = const.directory + const.timestr + '/' + v + '.csv'
        if not os.path.isfile(name):
            print 'File %s not present. Please download.' % name
            exit(0)

    name = const.directory + const.timestr + '/' + basket[0] + '.csv'
    first_stock = pd.read_csv(name, names=columns, skiprows=1,comment=comment, index_col='Date')
    print first_stock.head()
    first_stock.dropna()
    print 'Read successful: %s' % name
    for i in range(1,len(basket)):
        _ = const.directory + const.timestr + '/' + basket[i] + '.csv'
        dfstock = pd.read_csv(_, names=columns, skiprows=1,comment=comment, index_col='Date')
        dfstock.dropna()
        print 'Read successful: %s' % _
        if i == 1:
            data = pd.concat([first_stock['Settle'].rename(basket[0]),
                              dfstock['Settle'].rename(basket[i])],
                             axis=1, sort=False)
        else:
            data = pd.concat([data, dfstock['Settle'].rename(basket[i])],
                             axis=1, sort=False)

    data.replace([np.inf, -np.inf], np.nan).dropna()
    data = data.dropna(how='any')
    tocsv(name=const.filename_for_merge_futures, data=data)

    return data

def tocsv(data,name=None):

    if not os.path.exists(const.directory):
        os.makedirs(const.directory)


    if name is None:
        filename = const.directory + data.name+".csv"
    else:
        filename = const.directory + const.timestr + "/" +name + ".csv"
    try:
        if not os.path.exists(const.directory+const.timestr):
            os.makedirs(const.directory+const.timestr)
        data.to_csv(filename)
        print 'Created file: %s' % filename
    except Exception, e:
        print e


def main():
    parser = argparse.ArgumentParser(description='Pairs strategy for stocks')
    parser.add_argument('-d', '--delta', help='No. of days of history to pull', required=False, default=300)
    args = vars(parser.parse_args())


    data = pulldata(delta=args['delta'])
    filename = '%s_%s.csv' % ('usfutures', const.timestr)
    #convert_to_continuous(delta = args['delta'])
    #merge_basket_frames(basket=const.futures)
    # Run Linear regression on all the possible pairs in basket and create a csv file
    _name = pairTrader.LRegression_allPairs(data, filename)
    # Filter the above csv file and only show qualifying trades
    pairTrader.LRegression_qualifiedPairs1(data, _name)


if __name__=="__main__":
    main()
