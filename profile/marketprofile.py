import os
import matplotlib.pyplot as plt
import market_profile as mp
import numpy as np
import pandas as pd
import datetime, time
import argparse

def round_float(digits):
    def f(x):
        return round(np.float32(x), digits)
    return f

def read_pi_data(file_path, nifty=False):

    #define the frequency or interval for the collected data
    interval = 1800 #(60*interger, 60*30)
    columns = ['Timestamp','Open','High','Low','Close','Volume']
    if nifty:
        columns = ['Stock','YYYYMMDD','Timestamp','Open','High','Low','Close','Volume','_']
    try:

        data = pd.read_csv(file_path, skiprows=1, header=None,
                           names=columns,
                           converters={'Timestamp': np.str,
                                       'Open': round_float(4),
                                       'High': round_float(4),
                                       'Low': round_float(4),
                                       'Close': round_float(4),
                                       'Volume': np.int32})
    except Exception,e:
        print('File does not exist in location %s' % file_path)
        exit(1)
    # Reformat into a pandas dataframe with the date sequence as an index
    #data.set_index('Timestamp', inplace=True)
    #data.drop('Timestamp', axis=1, inplace=True)

    return data

def main():
    parser = argparse.ArgumentParser(description=
                                     'Pairs strategy for stocks')
    parser.add_argument('-n', '--nifty', help='Flag for NIFTY index',
                        required=False, action='store_true',
                        default=False)
    parser.add_argument('-z', '--zerodha', help='Flag for Zerodha Pi',
                        required=False, action='store_true',
                        default=False)
    parser.add_argument('-s', '--stock', help='Stock ticker',
                        required=False,
                        default='NIFTY')
    args = vars(parser.parse_args())

    #directory_name = "C:\Users\\abhi\\Documents\\projects\\py-market-profile\\tests\\fixtures\\"
    #filename = "google.csv"
    #directory_name = "C:\\Users\\abhi\\Downloads\\"

    if args['zerodha']:
        directory_name = "C:\\Zerodha\\Pi\\Exported\\"
        filename = "%s-EQ.csv" % args['stock']
        date_format = '%Y-%m-%d'
    elif args['nifty']:
        directory_name = "C:\\Users\\abhi\\Downloads\\26FEB\\"
        filename = '%s.txt' % args['stock']
        date_format = '%Y-%m-%d'


    """df = read_pi_data(file_path=directory_name+filename)
    mp1 = mp.MarketProfile(df, tick_size=1, mode='tpo')
    print 'data=', df.index.max()
    mp_slice = mp1[df.index.max() - pd.Timedelta(6, 'h'):df.index.max()]
    print mp_slice.profile
    """
    full_df = read_pi_data(file_path=directory_name+filename, nifty=args['nifty'])
    print full_df.head()
    #full_df.index = pd.to_datetime(full_df.index)
    full_df['Weekday'] = pd.to_datetime(full_df.Timestamp).dt.day_name()


    today = datetime.datetime.today().strftime(date_format)
    base = datetime.datetime.strptime(today, date_format)
    numdays = 7
    date_list = [(base - datetime.timedelta(days=x)).strftime(date_format) for x in range(0, numdays, 7) ]

    for day in date_list:
        print day
        print('\nTPO profile')

        mask = (pd.to_datetime(full_df.Timestamp).dt.week == pd.to_datetime(day).week)
        new_df = full_df.loc[mask]
        mp1 = mp.MarketProfile(new_df, tick_size=1, mode='tpo')
        new_df.set_index(pd.DatetimeIndex(new_df.Timestamp), inplace=True)
        mp_slice = mp1[5]
        print "POC: %f" % mp_slice.poc_price
        print "VAH: %f" % mp_slice.value_area[1]
        print "VAL: %f" % mp_slice.value_area[0]


        #VolumeProfile
        print('\nVolume Profile')
        mask = (pd.to_datetime(full_df.Timestamp).dt.week == pd.to_datetime(day).week)
        new_df = full_df.loc[mask]
        mp1 = mp.MarketProfile(new_df, tick_size=.05)
        new_df.set_index(pd.DatetimeIndex(new_df.Timestamp), inplace=True)
        mp_slice = mp1[5]
        print "POC: %f" % mp_slice.poc_price
        print "VAH: %f" % mp_slice.value_area[1]
        print "VAL: %f" % mp_slice.value_area[0]


    """
    for day in date_list:
        mask = (pd.to_datetime(full_df.Timestamp).dt.week == pd.to_datetime(day).week)
        print 'Mask type',type(mask)
        new_df = full_df.loc[mask]
        print new_df
        mp1 = mp.MarketProfile(new_df, tick_size=1, mode='tpo')
        new_df.set_index(pd.DatetimeIndex(new_df.Timestamp), inplace=True)
        print 'Index Max=',new_df.index.max(),'Index Min=',new_df.index.min()
        #mp_slice = mp1[new_df.index.max() - pd.Timedelta(6, 'h'):new_df.index.max()]
        mp_slice = mp1[new_df.index.min():new_df.index.max()]
        #mp_slice = mp1[mask]
        print mp_slice
        print "POC: %f" % mp_slice.poc_price
        print "Value area: %f, %f" % mp_slice.value_area
    """
    #Show a plot
    #data = mp_slice.profile
    #data.plot(kind='bar')

    #plt.show()
if __name__ == "__main__":
    main()