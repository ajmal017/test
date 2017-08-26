import datetime as dt
import pandas as pd
import numpy as np
import os,sys, time
import matplotlib.pyplot as plt
import argparse
from nsepy import get_history, get_index_pe_history
import datetime

class constants:

    rrate = 6.1495
    basket = ['ACC','ADANIPORTS','AMBUJACEM','ASIANPAINT','AXISBANK','BAJAJ-AUTO','BANKBARODA',
    'BHEL','BPCL','BHARTIARTL','BOSCHLTD','AUROPHARMA','CIPLA','COALINDIA','DRREDDY','GAIL','GRASIM',
    'HCLTECH','HDFCBANK','HEROMOTOCO','HINDALCO','HINDUNILVR','HDFC','ITC','ICICIBANK','IDEA','INDUSINDBK','INFY',
    'KOTAKBANK','LT','LUPIN','M&M','MARUIT','NTPC','ONGC','POWERGRID','INFRATEL','RELIANCE','SBIN',
    'SUNPHARMA','TCS','TATAMOTORS','TATAPOWER','TATASTEEL','TECHM','ULTRATECH','EICHERMOT','WIPRO','YESBANK',
    'ZEEL','TATAMTRDVR']
    expiry_cal = ['31082017', '28092017', '26102017']
    holiday = ['26012017', '24022017', '13032017', '28032017', '04042017', '14042017'
        , '01052017', '10052017', '26062017', '15082017', '17082017', '25082017'
        , '02102017', '10102017', '20102017', '01122017', '25122017']
    nDays = 365
    pass



def main():
    parser = argparse.ArgumentParser(description='Future spread calculator')
    parser.add_argument('-s', '--stock', help='NSE stock symbol', required=True)
    args = vars(parser.parse_args())

    format = '%d%m%Y'
    format1 = '%d/%m/%y'
    todays_date = dt.date.today().strftime(format)

    #directory = '/Users/abhishek.chaturvedi/PycharmProjects/self/test/data/%s' % todays_date
    directory = 'C:\\Users\\abhishek\\PycharmProjects\\test\\data\\%s' % todays_date

    if not os.path.isdir(directory):
        os.makedirs(directory)
    filename = 'CMVOLT_'
    lookbackdays = 20
    t_delta = dt.timedelta(days=lookbackdays)
    eTime = dt.date.today()
    oTime = eTime - t_delta
    #dates = pd.date_range(start=oTime, end=eTime, freq='B').format(formatter=lambda x: x.strftime(format))


    headers=['Date','Symbol','Settle Price',
             'PrevClose','LNReturn','PrevDV','CurrentDV',
             'AnnualV']

    #df = pd.read_csv(directory+'\..\CMVOLT_08082017.csv',names=headers,skiprows=1)

    #for eachstock in basket:
    #    print df[df['Symbol'] == eachstock]['Symbol']
    #    print df[df['Symbol']==eachstock]['CurrentDV']

    # Initialize
    lookbackdays = 60
    start_date = dt.date(2017,6,30)
    t_delta = dt.timedelta(days=lookbackdays)
    eTime = dt.date.today()
    oTime = eTime - t_delta
    dates = pd.date_range(start=start_date, end=eTime, freq='B').format(formatter=lambda x: x.strftime(format))

    #Stock history
    tick = args['stock']
    if os.path.isfile(directory+'\\%s_current.csv' % tick):
        current = pd.read_csv(directory + '\\%s_current.csv' % tick)
        mid = pd.read_csv(directory + '\\%s_mid.csv' % tick)
        #mid.Settle Price = mid.Settle Price.shift(-1)
    else:
        #stock = get_history(symbol=tick,start=oTime, end=eTime)
        current = get_history(symbol=tick,start=start_date, end=eTime,
                               index=False,futures=True,
                               expiry_date=dt.date(2017,8,31))
        current.to_csv(directory+'\\%s_current.csv' % tick)
        mid = get_history(symbol=tick,start=start_date, end=eTime,
                               index=False,futures=True,
                               expiry_date=dt.date(2017,9,28))
        #mid.Settle Price = mid.Settle Price.shift(1)

        mid.to_csv(directory+'\\%s_mid.csv' % tick)
        current['Date'] = current.index
        #Calculation for Tick difference (SPREAD)


    #cme = dt.datetime.strptime(constants.expiry_cal[0], format)
    #today = dt.date.today()
    #near['CME'] = pd.to_datetime(cme)

    #Calculate the Days to expiry datetime object

    current['DTE'] = current['Expiry'].apply(pd.to_datetime) - current['Date'].apply(pd.to_datetime)
    #Convert to number of days left to expiry
    current['DTE'] = current['DTE']/ np.timedelta64(1,'D')
    current['fairprice'] = current['Underlying']*(1 + constants.rrate*(current['DTE']/constants.nDays)/100)
    current.fillna(0,inplace=True)
    mid.fillna(0,inplace=True)
    columns = ['Date','fairprice','current_price','middle_price','Spread_cm','DTE']
    merge = pd.DataFrame(columns=columns)
    merge['Date']=current['Date']
    merge['DTE'] = current['DTE']
    merge['Spread_cm'] = current['Open'] - mid['Open']
    merge['fairprice'] = current['fairprice'].apply(lambda x: round(x,2))
    merge['Diff'] = merge['fairprice'] - current['Open']

    merge['current_price'] = current['Open']
    merge['middle_price'] = mid['Open']
    merge['mid_O'] = mid['Open']
    merge['current_O'] = current['Open']
    merge['mid_H'] = mid['High']
    merge['current_H'] = current['High']
    merge['mid_L'] = mid['Low']
    merge['current_L'] = current['Low']
    merge['mid_OI'] = mid['Open Interest']

    merge.fillna(0,inplace=True)
    merge.to_csv(directory+'\\%s_merge.csv' %(tick))
    print merge


    #expiry_cal = ['27012017','23022017','30032017','27042017']


    #Plot
    #near['Spread'].plot(marker='.')
    #stock_farmonth[['Settle Price','Underlying']].plot(colormap='jet', marker='.',title='FarMonth')
    #stock_nearmonth[['Settle Price','Underlying']].plot(colormap='jet', marker='.',title='NearMonth')
    #ax1 = stock_nearmonth['Settle Price'].plot()
    #stock_nearmonth['Underlying'].plot(ax=ax1)
    #stock_farmonth['Settle Price'].plot(ax=ax1)
    #plt.show()



if __name__ == '__main__':
    main()