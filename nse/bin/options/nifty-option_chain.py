import requests
from bs4 import BeautifulSoup
import mibian
import numpy as np
import datetime as dt

# Constants
dir = "C:/Users/abhi/Documents/projects/test/nse/bin/options"
ir = 7.0
lotsize = 75
today = dt.datetime.now().date()
end = dt.date(2019, 6, 27)

def get_days_to_expiry(today, end):
    return np.busday_count(today, end)


# Get all get possible expiry date details for the given script
def get_expiry_from_option_chain (symbol):

    # Base url page for the symbole with default expiry date
    Base_url = "https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol=" + symbol + "&date=-"

    # Load the page and sent to HTML parse
    page = requests.get(Base_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Locate where expiry date details are available
    locate_expiry_point = soup.find(id="date")
    # Convert as rows based on tag option
    expiry_rows = locate_expiry_point.find_all('option')

    index = 0
    expiry_list = []
    for each_row in expiry_rows:
        # skip first row as it does not have value
        if index <= 0:
            index = index + 1
            continue
        index = index + 1
        # Remove HTML tag and save to list
        expiry_list.append(BeautifulSoup(str(each_row), 'html.parser').get_text())

    # print(expiry_list)
    return expiry_list # return list


def _get_strike_price_from_option_chain(symbol, expdate):

    Base_url = "https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol=" + symbol + "&date=" + expdate

    page = requests.get(Base_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table_cls_2 = soup.find(id="octable")
    req_row = table_cls_2.find_all('tr')

    strike_price_list = []

    for row_number, tr_nos in enumerate(req_row):

        # This ensures that we use only the rows with values
        if row_number <= 1 or row_number == len(req_row) - 1:
            continue

        td_columns = tr_nos.find_all('td')
        strike_price = int(float(BeautifulSoup(str(td_columns[11]), 'html.parser').get_text()))
        strike_price_list.append(strike_price)

    # print (strike_price_list)
    return strike_price_list


def get_req_row(symbol, expdate):
    """
    Get the requested row from NSEINDIA webpage
    :param symbol: Symbol of interest
    :param expdate: Option expiry date
    :return: string
    """
    Base_url = "https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol=" + symbol + "&date=" + expdate

    page = requests.get(Base_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table_cls_2 = soup.find(id="octable")
    return table_cls_2.find_all('tr')

def get_put_askqty(symbol, exp_date):
    req_row = get_req_row(symbol, exp_date)
    put_askqty_list = []
    for row_number, tr_nos in enumerate(req_row):
        # This ensures that we use only the rows with values
        if row_number <= 1 or row_number == len(req_row) - 1:
            continue

        td_columns = tr_nos.find_all('td')
        try:
            char = BeautifulSoup(str(td_columns[13]),
                                 'html.parser').get_text(strip=True)
            if char == '-':
                askqty = float(0.0)
            else:
                askqty = float(str(BeautifulSoup(str(td_columns[12]),
                                                 'html.parser').get_text(strip=True)).replace(',', ''))
        except Exception as e:
            print(e)
        put_askqty_list.append(askqty)

    # print (strike_price_list)
    return put_askqty_list


mapper = {
    'oiC': 1,
    'chgoiC': 2,
    'volumeC': 3,
    'ivC': 4,
    'ltpC': 5,
    'netchgC': 6,
    'bidqtyC': 7,
    'bidpriceC': 8,
    'askpriceC': 9,
    'askqtyC': 10,
    'strike': 11,
    'bidqtyP': 12,
    'bidpriceP': 13,
    'askpriceP': 14,
    'askqtyP': 15,
    'netchgP': 16,
    'ltpP': 17,
    'ivP': 18,
    'volumeP': 19,
    'chgoiP': 20,
    'oiP': 21
}


def parse_chain(req_row, type=None):
    """
    get the values for option chain columns (type) from the parsed row (req_row)
    :param req_row: Parsed row from Option chain (html parser)
    :param type: Option Chain columns (mapper dictionary key items)
    :return: list
    """

    req_row = req_row
    bidqty_list = []
    if type not in mapper.keys():
        print('Wrong input for type.')
        exit(0)
    pos = mapper[type]

    # Populate the list with option chain data
    for row_number, tr_nos in enumerate(req_row):
        # This ensures that we use only the rows with values
        if row_number <= 1 or row_number == len(req_row) - 1:
            continue
        td_columns = tr_nos.find_all('td')
        _num = 0.0
        try:
            char = str(BeautifulSoup(str(td_columns[pos]), 'html.parser').get_text(strip=True)).replace(',', '')
            if char == '-':
                _num = float(0.0)
            else:
                _num = float(char)
        except Exception as e:
            print(e)
        bidqty_list.append(_num)

    return bidqty_list

def calculate_greeks(strike_list, call_iv_list, put_iv_list):
    """
    Calculate the option greeks
    :param strike_list: List of Strike prices
    :param iv_list: List of Implied Volatility
    :return:
    """

    call_delta = []
    put_delta = []

    for key, civ, piv in zip(strike_list, call_iv_list, put_iv_list):
        print(key, civ, piv)
    return call_delta, put_delta


spot = 11945
symbol = 'NIFTY'
dte = get_days_to_expiry(today, end)
list_expiries = get_expiry_from_option_chain(symbol)
req_row = get_req_row(symbol, expdate='27JUN2019')
for type in mapper.keys():
    pass
    #print(type , parse_chain(req_row=req_row, type=type))

print(calculate_greeks(parse_chain(req_row, type='strike'), parse_chain(req_row, 'ivC'), parse_chain(req_row, 'ivP')))





