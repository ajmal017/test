# -*- coding: utf-8 -*-
"""
Created on August 14
author : @abhishek
"""
import requests
#import urllib.request
#from urllib.request import urlopen
import sys, time, os
import re
import datetime
import calendar

#variables
class constants:

    pfilter = 0.02
    front_expiry = '2019,04,25'
    back_expiry = '2019,05,30'
    start_day = '2018,08,01'
    end_day = '2019,04,04'
    expiry_date = datetime.date(2019,04,25)
    expiry_month = 'Apr'
    timestr = time.strftime("%Y%m%d")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    location = script_dir + '/../../data/'
    log_location = location + 'log/'
    directory_name = location + timestr + '/'
    current_filename = directory_name + '../open_trades/current.csv'
    index=['NIFTY','BANKNIFTY']
    niftyauto = ['AMARAJABAT','APOLLOTYRE','ASHOKLEY','BAJAJ-AUTO','BHARATFORG','BOSCHLTD','EICHERMOT','EXIDEIND',
                  'HEROMOTOCO','MRF','M&M','MARUTI','MOTHERSUMI','TVSMOTOR','TATAMTRDVR','TATAMOTORS']
    niftyit = ['HCLTECH', 'INFIBEAM', 'INFY', 'KPIT', 'MINDTREE', 'OFSS', 'TCS', 'TATAELXSI', 'TECHM', 'WIPRO']
    niftymetal = ['APLAPOLLO', 'COALINDIA', 'HINDALCO', 'HINDCOPPER', 'HINDZINC', 'JSWSTEEL',
              'JSLHISAR', 'JINDALSTEL', 'MOIL', 'NMDC', 'NATIONALUM', 'SAIL', 'TATASTEEL', 'VEDL', 'WELCORP']
    banknifty = ['BANKNIFTY','AXISBANK','BANKBARODA','HDFCBANK','ICICIBANK',
                 'INDUSINDBK','KOTAKBANK',
                 'PNB','RBLBANK','SBIN','YESBANK']
    nifty50 = ['ACC','ADANIPORTS','AMBUJACEM','ASIANPAINT','AXISBANK','BAJAJ-AUTO','BANKBARODA',
    'BHEL','BPCL','BHARTIARTL','BOSCHLTD','AUROPHARMA','CIPLA','COALINDIA','DRREDDY','GAIL','GRASIM',
    'HCLTECH','HDFCBANK','HEROMOTOCO','HINDALCO','HINDUNILVR','HDFC','ITC','ICICIBANK','IDEA','INDUSINDBK','INFY',
    'KOTAKBANK','LT','LUPIN','M&M','MARUTI','NTPC','ONGC','POWERGRID','INFRATEL','RELIANCE','SBIN',
    'SUNPHARMA','TCS','TATAMOTORS','TATAPOWER','TATASTEEL','TECHM','ULTRATECH','EICHERMOT','WIPRO','YESBANK',
    'ZEEL','TATAMTRDVR']
    usfutures = ['esu18','clv18','gcz18','nqu18']
    grains = ['ZC','ZS','ZW','ZL','ZM','ZO','XK','XW','XC']
    METALS = ['GC','HG','SI','PL','PA','MGC','YG','YI']
    #ENERGY = ['BRN','NG','CL','HO','RB','QM','WBS','BZ','QG']
    ENERGY = ['cbx18','clv18','clx18']
    INDICES = ['esu18','nqu18','ymu18']
    mBasket = ['AAPL','AMD','MU','NVDA','PEP','COKE']
    bnifty_lotsize = {'AXISBANK':1200, 'BANKBARODA': 4000,'HDFCBANK':500,'ICICIBANK':2750,
                      'IDFCBANK':11000,'INDUSINDBK':300,'KOTAKBANK': 800,'PNB':5500,'RBLBANK':1200,
                      'SBIN':3000,'YESBANK':1750,'BANKNIFTY':40}
    header = ['YStock', 'XStock', 'PValue', 'Beta', 'STD_ERR_Ratio', 'Alpha', 'Close_STD_Error', 'Alpha:YPrice']


# utility class implementing the helper funtions for nsequoter
# all functions are weakly private
class Utils():
    _base_url = "https://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol="
    _FO_url = "https://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuoteFO.jsp?underlying="
    _months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    _now = datetime.date.today()
    _month = _now.month
    _year = _now.year
    _date = _now.day
    _weekday = _now.isoweekday()
    _codes = {}  # constructor will build this with stocks currently traded on the nse

    # cunstructor
    def __init__(self):
        self._build_codes_dict()

    # getting the requested page to be scraped and raising exceptions when valid
    def _get_page_or_exception(self, url):

        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        try:
            #r = requests.get(url, headers=hdr)
            r = urllib.request.Request(url, headers=hdr)
            content = urllib.request.urlopen(r).read()
        except requests.exceptions.ConnectionError as e:
            print (e)
            sys.exit(1)
        except requests.exceptions.Timeout as e:
            print (e)
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print (e)
            sys.exit(1)
        #if r.status_code != 200:
        #    r.raise_for_status()
        return content
        #return r

    # for equity derivatives
    def _get_last_thursday(self, y, mon):

        days = calendar.monthrange(y, mon)
        dt = datetime.date(y, mon, days[1])
        offset = 4 - dt.isoweekday()
        if offset > 0: offset -= 7
        dt += datetime.timedelta(offset)
        return dt.day

    # for currency derivatives (to be implemented in the next version)
    def _get_last_wednesday(self, y, mon):

        days = calendar.monthrange(y, mon)
        dt = datetime.date(y, mon, days[1])
        offset = 3 - dt.isoweekday()
        if offset > 0: offset -= 7
        dt += datetime.timedelta(offset)
        return dt.day

    # builds the dictionary of curently traded stock codes
    def _build_codes_dict(self):
        url = 'https://www.nseindia.com/content/equities/EQUITY_L.csv'
        r = self._get_page_or_exception(url)
        items = r.splitlines()
        for i in range(len(items)):
            items[i] = items[i].split(',')
        for i in range(len(items)):
            self._codes[items[i][0]] = items[i][1]

    # based on parameters, build the right url to be scraped and scrapes it
    def get_quote(self, eq, cont='EQ', mon=_month,search_string='lastPrice'):

        eq = eq.upper()
        if eq not in self._codes:
            raise Exception('Invalid Symbol/Code!')

        if cont == 'EQ':
            url = self._base_url + eq.upper()

        elif cont == 'FUTSTK':
            if type(mon) == int:
                mon == self._months[mon - 1]
            else:
                mon = mon.upper()
            if ((self._months.index(mon) + 1) > ((self._month + 2) % 12)) or (
                (self._months.index(mon) + 1) < self._month):
                raise Exception('Contract not available!')
            y = self._year
            if (self._month == 'DEC') and (mon == 'JAN' or 'FEB'): y += 1
            d = self._get_last_thursday(y, (self._months.index(mon) + 1))
            if self._date > d:
                raise Exception('Contract Expired!')
            url = self._FO_url + eq + '&instrument=FUTSTK&expiry=' + str(d) + mon + str(y)
        elif cont == 'FUTIDX':
            if type(mon) == int:
                mon == self._months[mon - 1]
            else:
                mon = mon.upper()
            if ((self._months.index(mon) + 1) > ((self._month + 2) % 12)) or (
                (self._months.index(mon) + 1) < self._month):
                raise Exception('Contract not available!')
            y = self._year
            if (self._month == 'DEC') and (mon == 'JAN' or 'FEB'): y += 1
            d = self._get_last_thursday(y, (self._months.index(mon) + 1))
            if self._date > d:
                raise Exception('Contract Expired!')
            url = self._FO_url + eq + '&instrument=FUTIDX&expiry=' + str(d) + mon + str(y)
        else:
            raise Exception('Facility not available yet!')

        pattern = r'"%s":"(\d*,?\d*\.\d*)"' %search_string
        r = self._get_page_or_exception(url)
        match = re.findall(pattern, r.text)
        quote = match[0].replace(',', '')
        return float(quote)

    def get_open(self, eq, cont='EQ', mon=_month):

        eq = eq.upper()
        if eq not in self._codes:
            raise Exception('Invalid Symbol/Code!')

        if cont == 'EQ':
            url = self._base_url + eq.upper()

        elif cont == 'FUTSTK':
            if type(mon) == int:
                mon == self._months[mon - 1]
            else:
                mon = mon.upper()
            if ((self._months.index(mon) + 1) > ((self._month + 2) % 12)) or (
                (self._months.index(mon) + 1) < self._month):
                raise Exception('Contract not available!')
            y = self._year
            if (self._month == 'DEC') and (mon == 'JAN' or 'FEB'): y += 1
            d = self._get_last_thursday(y, (self._months.index(mon) + 1))
            if self._date > d:
                raise Exception('Contract Expired!')
            url = self._FO_url + eq + '&instrument=FUTSTK&expiry=' + str(d) + mon + str(y)
        elif cont == 'FUTIDX':
            if type(mon) == int:
                mon == self._months[mon - 1]
            else:
                mon = mon.upper()
                print mon
            if ((self._months.index(mon) + 1) > ((self._month + 2) % 12)) or (
                (self._months.index(mon) + 1) < self._month):
                raise Exception('Contract not available!')
            y = self._year
            if (self._month == 'DEC') and (mon == 'JAN' or 'FEB'): y += 1
            d = self._get_last_thursday(y, (self._months.index(mon) + 1))
            if self._date > d:
                raise Exception('Contract Expired!')
            url = self._FO_url + eq + '&instrument=FUTIDX&expiry=' + str(d) + mon + str(y)
            print url
        else:
            raise Exception('Facility not available yet!')

        pattern = r'"open":"(\d*,?\d*\.\d*)"'
        r = self._get_page_or_exception(url)
        match = re.findall(pattern, r.text)
        quote = match[0].replace(',', '')
        return float(quote)

    def get_open(self, eq, cont='EQ', mon=_month):

        eq = eq.upper()
        if eq not in self._codes:
            raise Exception('Invalid Symbol/Code!')

        if cont == 'EQ':
            url = self._base_url + eq.upper()

        elif cont == 'FUTSTK':
            if type(mon) == int:
                mon == self._months[mon - 1]
            else:
                mon = mon.upper()
            if ((self._months.index(mon) + 1) > ((self._month + 2) % 12)) or (
                (self._months.index(mon) + 1) < self._month):
                raise Exception('Contract not available!')
            y = self._year
            if (self._month == 'DEC') and (mon == 'JAN' or 'FEB'): y += 1
            d = self._get_last_thursday(y, (self._months.index(mon) + 1))
            if self._date > d:
                raise Exception('Contract Expired!')
            url = self._FO_url + eq + '&instrument=FUTSTK&expiry=' + str(d) + mon + str(y)
        elif cont == 'FUTIDX':
            if type(mon) == int:
                mon == self._months[mon - 1]
            else:
                mon = mon.upper()
            if ((self._months.index(mon) + 1) > ((self._month + 2) % 12)) or (
                (self._months.index(mon) + 1) < self._month):
                raise Exception('Contract not available!')
            y = self._year
            if (self._month == 'DEC') and (mon == 'JAN' or 'FEB'): y += 1
            d = self._get_last_thursday(y, (self._months.index(mon) + 1))
            if self._date > d:
                raise Exception('Contract Expired!')
            url = self._FO_url + eq + '&instrument=FUTIDX&expiry=' + str(d) + mon + str(y)
        else:
            raise Exception('Facility not available yet!')

        pattern = r'"open":"(\d*,?\d*\.\d*)"'
        r = self._get_page_or_exception(url)
        match = re.findall(pattern, r.text)
        quote = match[0].replace(',', '')
        return float(quote)