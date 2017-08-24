import time as t
import argparse
import pandas as pd
import datetime as dt

def pullData(stock):

    holiday = ['26012017','24022017','13032017','28032017','04042017','14042017'
               ,'01052017','10052017','26062017','15082017','17082017','25082017'
               ,'02102017','10102017','20102017','01122017','25122017']

    expiry_cal = ['27012017','23022017','30032017','27042017']

    try:
        print 'Currently trying to pull: ', stock
        print 'Current time is: ',str(dt.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S'))
        file = 'C:\\Users\\abhishek\\Downloads\\stocks\\DownloadData\\FOVOLT_%s.csv' % expiry_cal[0]
        column=['date','symbol','Price','pClose','LogReturn','prevDVol','currentDVol','underAVol','futCPrice','futprevCPrice','futLogReturn','prevfDVol'
                 ,'curfDVol','futAVol','appDVol','applAVol']
        df = pd.read_csv(file, skiprows=1, names=column)
        print df[df['symbol']==stock]

        """
        # CODE FOR CALCULATING EXPIRY
        today = dt.datetime.today()
        for i in range(6):
            expiry_date = today + relativedelta(weekday=TH(i))

            if expiry_date.month != today.month:
                # since t is exceeded we need last one  which we can get by subtracting -2 since it is already a Thursday.
                expiry_date = expiry_date + relativedelta(weekday=TH(-2))
                break
        expDate = expiry_date.strftime('%d%m%Y')
        print 'Expiry may be on:', expDate
        expDate = calendar.Calendar(3).monthdatescalendar(2017, 3)[4][0].strftime('%d%m%Y')
        print expDate
        """
    except Exception,e:
        print str(e)

def main():
    parser = argparse.ArgumentParser(description='STOCK volatility calculator')
    parser.add_argument('-s', '--stock', help='NSE stock symbol', required=True)
    args = vars(parser.parse_args())

    pullData(stock=args['stock'])

if __name__ == '__main__':
    main()