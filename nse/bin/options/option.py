
import mibian
import numpy as np
from util import *
import datetime as dt
import pandas as pd

greek_columns = ['delta','theta','vega','gamma']
df_call_columns = ['OI','Chng in OI','Volume','IV','LTP','Net Chng',
'Bid Qty','Bid Price','Ask Price','Ask Qty','Strike_Price','delta','theta','vega','gamma']
df_put_columns = ['Strike_Price','Bid Qty','Bid Price','Ask Price','Ask Qty','Net Chng','LTP',
'IV','Volume','Chng in OI','OI','delta','theta','vega','gamma']

path = "C:/Users/abhi/Documents/projects/test/nse/bin/options"
calldf = pd.read_csv(path + '/call-test.csv',names=df_call_columns,na_values='-',delim_whitespace=True)
calldf.columns = calldf.columns.str.strip()
calldf = calldf.dropna(subset=['IV','Ask Price','Bid Price'])
#print(calldf.head())

putdf = pd.read_csv(path + '/put-test.csv',names=df_put_columns,na_values='-',delim_whitespace=True)
putdf.columns = putdf.columns.str.strip()
putdf = putdf.dropna(subset=['IV','Ask Price','Bid Price'])
#print(putdf.head())

spot=11924.75
today = dt.datetime.now().date()
end = dt.date(2019, 6, 27)
dte = np.busday_count(today, end)
print("DTE: %s" % dte)
ir = 7

def round(num):
    _round = 2

    return str(np.round(num, _round))




class option():
    """
    Call/Put options value
    """
    def __init__(self, df_row):
        #parameter is a row from the dataframe
        self.dte = dte
        self.ir = ir
        self.df_row = df_row
        self.option = mibian.BS([spot, df_row['Strike_Price'], self.ir, self.dte],
                                volatility=df_row['IV'])

    def callDelta(self):
        return np.round(self.option.callDelta,2)

    def putDelta(self):
        return np.round(self.option.putDelta,2)

    def positionDelta(self):
        return np.round(self.option.putDelta + self.option.callDelta,2)

    def callTheta(self):
        return np.round(self.option.callTheta,2)

    def putTheta(self):
        return np.round(self.option.putTheta,2)

    def vega(self):
        return np.round(self.option.vega,2)

    def gamma(self):
        return np.round(self.option.gamma,2)



#print("Strike"+'\t'+"Delta"+'\t'+"Theta"+'\t'+"Vega"+'\t'+'Bid'+'\t'+'Ask')
#print("CALLS")
"""
def call_prices():
    for i,row in calldf.iterrows():
        copt = mibian.BS([spot, row['Strike_Price'], ir, dte], volatility=row['IV'])
        #popt = mibian.BS([spot, row['Strike_Price'], ir, dte], volatility=row['IV'])
        #print(round(row['Strike_Price'])+'\t'+round(copt.callDelta)
        #     + '\t' +round(copt.callTheta)+'\t'+round(copt.vega)
        #      + '\t' + row['Bid Price']+ '\t' + row['Ask Price'])
#print("PUTS")
def put_prices():
    for i,row in putdf.iterrows():
        popt = mibian.BS([spot, row['Strike_Price'], ir, dte], volatility=row['IV'])
        #print(round(row['Strike_Price'])+'\t'+round(popt.putDelta)
        #      + '\t' +round(popt.putTheta)+'\t'+round(popt.vega)
        #      + '\t' + row['Bid Price']+ '\t' + row['Ask Price'])


#pos_delta = 0 - put_option.putDelta - call_option.callDelta
#print("PutDelta=", np.round(0-put_option.putDelta,3))
#print("CallDelta=", np.round(0-call_option.callDelta,3))
#print("Position Delta = ", np.round(pos_delta,3))


tid=1
nifty_lot_size = 75
n_lots = 1
put_sold_price = [tid, 35, 0]
call_sold_price = [tid, 21.5,13.5]
#print(put_sold_price, call_sold_price)

#pl_open = ((call_sold_price[1]-call_sold_price[2]) + (put_sold_price[1]-put_sold_price[2]))*n_lots*nifty_lot_size
#print pl_open
"""