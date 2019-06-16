import requests
from bs4 import BeautifulSoup
from mibian import Me, BS
import numpy as np
import pandas as pd
from PyQt4 import QtCore, QtGui
import sys
import datetime as dt
import matplotlib
#matplotlib.use('gtkagg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor


# Constants
dir = "C:/Users/abhi/Documents/projects/test/nse/bin/options"
spot = 11823.3
symbol = 'NIFTY'

ir = 7.0
lotsize = 75
today = dt.datetime.now().date()
end = dt.date(2019, 6, 27)
leg1_strike = 11400
leg2_strike = 11400
leg3_strike = None
leg4_strike = None
future_buy_price = -11980
leg1_premium = 111.4
leg2_premium = 125
leg3_premium = 0.0
leg4_premium = 0.0

num_lots_futures = 1.0
num_lots_leg1 = 5.0
num_lots_leg2 = 15.0

Qt = QtCore.Qt


def get_days_to_expiry(today, end):
    return np.busday_count(today, end)


def strangle_payoff(dataFrame):
    """
    Calculate the payoff
    :param dataFrame: Input dataframe from option chain
    :return: dataframe
    """

    dataFrame['Spot'] = np.repeat(spot, dataFrame.__len__())
    dataFrame['leg1_intr_Value'] = np.maximum(dataFrame.strikes - leg1_strike, 0)
    dataFrame['leg1_premium'] = np.repeat(leg1_premium, dataFrame.__len__())
    if leg1_premium == 0.0:
        dataFrame['leg1Payoff'] = 0
    else:
        dataFrame['leg1Payoff'] = num_lots_leg1 * (dataFrame['leg1_premium'] - dataFrame['leg1_intr_Value'])

    dataFrame['leg2_intr_Value'] = np.maximum(leg2_strike - dataFrame.strikes, 0)
    dataFrame['leg2_premium'] = np.repeat(leg2_premium, dataFrame.__len__())

    if leg2_premium == 0.0:
        dataFrame['leg2Payoff'] = 0
    else:
        dataFrame['leg2Payoff'] = num_lots_leg2 * (dataFrame['leg2_premium'] - dataFrame['leg2_intr_Value'])
    dataFrame['Payoff'] = dataFrame['leg1Payoff'] + dataFrame['leg2Payoff']
    return dataFrame


def cross_hair(x, y, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()
    horiz = ax.axhline(y, **kwargs)
    vert = ax.axvline(x, **kwargs)
    return horiz, vert

def payoff(strike_list,*args):

    payoff_list = []

    """
    list[0] = strike
    list[1] = premium credit or debit
    list[2] = call or put
    list[3] = Long or Short
    list[4] = size of the trade
    """
    def price(list):
        """ return payoff for each leg of the trade"""
        if list[2].upper() == 'P':
            if list[3].upper() == 'L':
                payoff_leg = [list[4] * (max(0, list[0] - i) - list[1]) for i in strike_list]
            else:
                payoff_leg = [list[4] * (list[1] - max(0, list[0] - i)) for i in strike_list]
        else:
            if list[3].upper() == 'L':
                payoff_leg = [list[4] * (max(0, i - list[0]) - list[1]) for i in strike_list]
            else:
                payoff_leg = [list[4] * (list[1] - max(0, i - list[0])) for i in strike_list]

        return payoff_leg

    for arg in args:
        """ Add the payoff of each leg of the trade to a list """
        payoff_list.append(price(arg))

    payoff = np.sum(payoff_list, axis=0)

    return payoff


def get_credit_recvd(*args):
    """ Get the credit/debit for the strategy """
    credit = []
    debit = []
    for k, arg in enumerate(args):
        if arg[3].upper() == 'S':
            credit.append(int(arg[1] * int(arg[4])))
        else:
            credit.append(-(int(arg[1] * int(arg[4]))))

    total_credit = np.sum(credit)
    print('Total Credit in points: ', total_credit)
    print('Max profit: ', total_credit * 75)

def get_greeks_strategy(strike_list, *args):
    """ Get the gamma for each option strike in the chain """
    theta = []
    gamma = []
    delta = []
    vega = []
    for k, arg in enumerate(args):
        index = strike_list.index(args[k][0])
        if arg[2].upper() == 'P':
            theta.append(BS([spot, arg[0], ir, dte], volatility=put_iv_list[index]).putTheta)
            gamma.append(BS([spot, arg[0], ir, dte], volatility=put_iv_list[index]).gamma)
            delta.append(BS([spot, arg[0], ir, dte], volatility=put_iv_list[index]).putDelta)
            vega.append(BS([spot, arg[0], ir, dte], volatility=put_iv_list[index]).vega)
        else:
            theta.append(BS([spot, arg[0], ir, dte], volatility=call_iv_list[index]).callTheta)
            gamma.append(BS([spot, arg[0], ir, dte], volatility=call_iv_list[index]).gamma)
            delta.append(BS([spot, arg[0], ir, dte], volatility=call_iv_list[index]).callDelta)
            vega.append(BS([spot, arg[0], ir, dte], volatility=call_iv_list[index]).vega)

    snap_theta = np.round(np.sum(theta, axis=0),3)
    print('Theta: ', snap_theta)
    print('Vega: ', np.round(np.sum(vega),3))
    print('Delta: ', np.round(np.sum(delta),3))
    print('Gamma: ', np.round(np.sum(gamma),3))
    print('Total Decay:', snap_theta * 75 )

    return None


def get_gamma_option_chain(strike_list, **kwargs):
    """ Get the gamma for each option strike in the chain """

    gamma = []
    for args in kwargs:
        for key, value in enumerate(strike_list):
            vol = call_iv_list if args[2].upper() == 'C' else put_iv_list
            gamma.append(BS([spot, value, ir, dte], volatility=vol[key]).gamma)



def butterfly_payoff(dataFrame, strike1, strike1premium, strike2,
                     strike2premium, strike3=None, strike3premium=None,
                     strike4=None, strike4premium=None, type='call'):
    """
    Calculate the payoff
    :param dataFrame: Input dataframe from option chain
    :return: dataframe
    """

    dataFrame['Spot'] = np.repeat(spot, dataFrame.__len__())
    if type == 'put':
        dataFrame['leg1_intr_Value'] = np.maximum(strike1 - dataFrame.strikes, 0)
        dataFrame['leg2_intr_Value'] = np.maximum(strike2 - dataFrame.strikes, 0)
        dataFrame['leg3_intr_Value'] = np.maximum(strike3 if strike3 else 0.0 - dataFrame.strikes, 0)
        dataFrame['leg4_intr_Value'] = np.maximum(strike4 if strike4 else 0.0 - dataFrame.strikes, 0)
    if type == 'call':
        dataFrame['leg2_intr_Value'] = np.maximum(dataFrame.strikes - strike2, 0)
        dataFrame['leg1_intr_Value'] = np.maximum(dataFrame.strikes - strike1, 0)

    dataFrame['leg1_premium'] = np.repeat(strike1premium if strike1premium else 0.0, dataFrame.__len__())
    dataFrame['leg2_premium'] = np.repeat(strike2premium if strike2premium else 0.0, dataFrame.__len__())
    dataFrame['leg3_premium'] = np.repeat(strike3premium if strike3premium else 0.0, dataFrame.__len__())
    dataFrame['leg4_premium'] = np.repeat(strike4premium if strike4premium else 0.0, dataFrame.__len__())

    if leg1_premium == 0.0:
        dataFrame['leg1Payoff'] = 0
    else:
        dataFrame['leg1Payoff'] = num_lots_leg1 * (dataFrame['leg1_premium'] - dataFrame['leg1_intr_Value'])


    if leg2_premium == 0.0:
        dataFrame['leg2Payoff'] = 0
    else:
        dataFrame['leg2Payoff'] = num_lots_leg2 * (dataFrame['leg2_premium'] - dataFrame['leg2_intr_Value'])
    dataFrame['Payoff'] = dataFrame['leg1Payoff'] + dataFrame['leg2Payoff']
    return dataFrame


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

def calculate_greeks(strike_list, call_iv_list, put_iv_list, algo='BS'):
    """
    Calculate the option greeks
    :param strike_list: List of Strike prices
    :param iv_list: List of Implied Volatility
    :return:
    """
    call_delta = []
    call_theta = []
    put_delta = []
    put_theta = []
    vega = []
    gamma = []

    df = pd.DataFrame()

    if algo == 'ME':
        for k,value in enumerate(strike_list):
            call_theta.append(Me([spot, value, ir, dte], volatility=call_iv_list[k]).callTheta)
            call_delta.append(Me([spot, value, ir, dte], volatility=call_iv_list[k]).callDelta)
            put_delta.append(Me([spot, value, ir, dte], volatility=put_iv_list[k]).putDelta)
            put_theta.append(Me([spot, value, ir, dte], volatility=put_iv_list[k]).putTheta)

    else:
        for k,value in enumerate(strike_list):
            call_theta.append(BS([spot, value, ir, dte], volatility=call_iv_list[k]).callTheta)
            call_delta.append(BS([spot, value, ir, dte], volatility=call_iv_list[k]).callDelta)
            put_delta.append(BS([spot, value, ir, dte], volatility=put_iv_list[k]).putDelta)
            put_theta.append(BS([spot, value, ir, dte], volatility=put_iv_list[k]).putTheta)


    df['strikes'] = np.asarray(strike_list)
    df['callDelta'] = np.asarray(call_delta)
    df['callTheta'] = np.asarray(call_theta)
    df['IV_Call'] = np.asarray(call_iv_list)
    df['LTP_Call'] = np.asarray(call_ltp)
    df['putDelta'] = np.asarray(put_delta)
    df['putTheta'] = np.asarray(put_theta)
    df['IV_Put'] = np.asarray(put_iv_list)
    df['LTP_Put'] = np.asarray(put_ltp)

    return df


def get_itm_strikes(strike_list, option_type):
    """
    Get the ITM strikes for an list of strikes
    :param strike_list: List of strike prices
    :param option_type: Type of option (call or put)
    :return: list
    """
    itm_list = []

    if option_type == 'call':
        itm_list = [i for i in strike_list if i <= spot]
    if option_type == 'put':
        itm_list = [i for i in strike_list if i >= spot]

    return itm_list

def get_otm_strikes(strike_list, option_type='call'):
    """
    Get the ITM strikes for an list of strikes
    :param strike_list: List of strike prices
    :param option_type: Type of option (call or put)
    :return: list
    """
    otm_list = []
    if option_type == 'call':
        otm_list = [i for i in strike_list if i >= spot]
    if option_type == 'put':
        otm_list = [i for i in strike_list if i <= spot]

    return otm_list


class _PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data.values[index.row()][index.column()]))
        return QtCore.QVariant()

class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None

def qt_display(dataframe):
    application = QtGui.QApplication(sys.argv)
    view = QtGui.QTableView()
    model = PandasModel(df)
    view.setModel(model)

    view.show()
    #sys.exit(application.exec_())


def plot_payoff(payoff):
    fig = plt.figure(figsize=(10,10))
    ax1 = fig.add_subplot(2,1,1)
    ax1.plot(strike_list, payoff, label='Payoff All legs')
    ax1.legend(fontsize=8)
    ax1.set_xlabel('Strategy payoff', fontsize=8)
    #ax.set_xlim(spot-1000, spot+1000)
    #ax.set_ylim(-500, 500)
    ax1.axvline(spot, lw=1.0, linestyle='--', label='Spot')
    ax1.axhline(0, lw=1.0, linestyle='--', color='r')
    cursor = Cursor(ax1, useblit=True, color='red', linewidth=1.5)
    ax1.grid(True)

    ax2 = fig.add_subplot(223)
    ax2.plot(strike_list, call_iv_list, label='Call IV')
    ax2.legend(fontsize=8)
    ax2.grid(True)

    ax3 = fig.add_subplot(224)
    ax3.plot(strike_list, put_iv_list, label='Put IV')
    ax3.legend(fontsize=8)
    ax3.grid(True)

    return None


def trade_details(*args):
    _payoff = payoff(strike_list, *args)
    """
    qt_display(_calc_dataframe)
    """
    plot_payoff(payoff=_payoff)
    get_greeks_strategy(strike_list, *args)
    get_credit_recvd(*args)


if __name__ == '__main__':

    dte = get_days_to_expiry(today, end)
    list_expiries = get_expiry_from_option_chain(symbol)
    req_row = get_req_row(symbol, expdate='27JUN2019')


    strike_list = parse_chain(req_row, 'strike')
    call_iv_list = parse_chain(req_row, 'ivC')
    put_iv_list = parse_chain(req_row, 'ivP')
    call_bidprice = parse_chain(req_row, 'bidpriceC')
    put_bidprice = parse_chain(req_row, 'bidpriceP')
    call_askprice = parse_chain(req_row, 'askpriceC')
    put_askprice  = parse_chain(req_row, 'askpriceP')
    call_ltp = parse_chain(req_row, 'ltpC')
    put_ltp = parse_chain(req_row, 'ltpP')
    call_itm_strikes = get_itm_strikes(strike_list, 'call')
    call_otm_strikes = get_otm_strikes(strike_list, 'call')
    put_itm_strikes = get_itm_strikes(strike_list, 'put')
    put_otm_strikes = get_otm_strikes(strike_list, 'put')
    df = calculate_greeks(strike_list, call_iv_list, put_iv_list)

    #_calc_dataframe = strangle_payoff(dataFrame=df)
    #_calc_dataframe = butterfly_payoff(df, 12200, 111.4, 11500, 145)

    k1 = '11700PE'
    k2 = '12000CE'
    k3 = None
    k4 = None


    if k1:
        premium = put_ltp[strike_list.index(int(k1[:-2]))] if k1[-2:] == 'PE' \
            else call_ltp[strike_list.index(int(k1[:-2]))]
        leg1 = [int(k1[:-2]), premium , k1[-2:][0], 'S', 5]
        print('Leg1 premium:', premium)
    if k2:
        premium = put_ltp[strike_list.index(int(k2[:-2]))] if k2[-2:]=='PE' \
            else call_ltp[strike_list.index(int(k2[:-2]))]
        leg2 = [int(k2[:-2]), premium, k2[-2:][0], 'S', 5]
        print('Leg2 premium:', premium)
    if k3:
        premium = put_ltp[strike_list.index(int(k3[:-2]))] if k3[-2:]=='PE' \
            else call_ltp[strike_list.index(int(k3[:-2]))]
        leg3 = [int(k3[:-2]), premium, k3[-2:][0], 'S', 5]
        print('Leg3 premium:', premium)
    if k4:
        premium = put_ltp[strike_list.index(int(k4[:-2]))] if k4[-2:]=='PE' \
            else call_ltp[strike_list.index(int(k4[:-2]))]
        leg4 = [int(k4[:-2]), premium, k4[-2:][0], 'S', 5]
        print('Leg4 premium:', premium)

    trade_details(leg1, leg2)
    plt.show()
