from ib.ext.Contract import Contract
from ib.ext.Order import Order
#from ib.opt import Connection, message, ibConnection
import ib.opt

import sys
if sys.version_info.major == 2:
    import Queue as queue
else:
    import queue

def error_handler(msg):
    """Handles the capturing of error messages"""
    print "Server Error: %s" % msg

def reply_handler(msg):
    """Handles of server replies"""
    print "Server Response: %s, %s" % (msg.typeName, msg)


def handle_order_id(msg):
    global newOrderID
    newOrderID = msg.orderId


def create_contract(symbol, sec_type, exch, prim_exch, curr):
    """Create a Contract object defining what will
    be purchased, at which exchange and in which currency.

    symbol - The ticker symbol for the contract
    sec_type - The security type for the contract ('STK' is 'stock')
    exch - The exchange to carry out the contract on
    prim_exch - The primary exchange to carry out the contract on
    curr - The currency in which to purchase the contract"""
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = sec_type
    contract.m_exchange = exch
    contract.m_primaryExch = prim_exch
    contract.m_currency = curr
    return contract

def create_order(order_type, quantity, action):
    """Create an Order object (Market/Limit) to go long/short.

    order_type - 'MKT', 'LMT' for Market or Limit orders
    quantity - Integral number of assets to order
    action - 'BUY' or 'SELL'"""
    order = Order()
    order.m_orderType = order_type
    order.m_totalQuantity = quantity
    order.m_action = action
    return order

def make_contract(symbol, sec_type, exch, prim_exch, curr):
    Contract.m_symbol = symbol
    Contract.m_secType = sec_type
    Contract.m_exchange = exch
    Contract.m_primaryExch = prim_exch
    Contract.m_currency = curr
    return Contract

def make_order(action, quantity, price = None):
    if price is not None:
        order = Order()
        order.m_orderType = 'LMT'
        order.m_totalQuantity = quantity
        order.m_action = action
        order.m_lmtPrice = price

    else:
        order = Order()
        order.m_orderType = 'MKT'
        order.m_totalQuantity = quantity
        order.m_action = action

    return order


"""
if __name__ == "__main__":
    # Connect to the Trader Workstation (TWS) running on the
    # usual port of 7496, with a clientId of 100
    # (The clientId is chosen by us and we will need
    # separate IDs for both the execution connection and
    # market data connection)
    conn = Connection.create(port=7497, clientId=100)
    conn.connect()
    conn.reqMarketDataType(3)

    # Assign the error handling function defined above
    # to the TWS connection
    conn.register(error_handler, 'Error')
    conn.register(handle_order_id, 'NextValidId')

    # Receive the new orderID sequence from IB server

    # Assign all of the server reply messages to the
    # reply_handler function defined above
    conn.registerAll(reply_handler)

    # Create an order ID which is 'global' for this session. This
    # will need incrementing once new orders are submitted.
    #order_id = 9010

    # Create a contract in GOOG stock via SMART order routing
    cont = make_contract('TSLA', 'STK', 'SMART', 'SMART', 'USD')
    offer = make_order('BUY', 1, 200)

    # Use the connection to the send the order to IB
    conn.placeOrder(9012, cont, offer)

    # Disconnect from TWS
    conn.disconnect()
"""

class IbManager(object):
    def __init__(self, timeout=20, **kwargs):
        self.q = queue.Queue()
        self.timeout = 20

        self.con = ib.opt.ibConnection(**kwargs)
        self.con.registerAll(self.watcher)

        self.msgs = {
            ib.opt.message.error: self.errors,
            ib.opt.message.contractDetails: self.contractDetailsHandler,
            ib.opt.message.contractDetailsEnd: self.contractDetailsHandler
        }

        self.skipmsgs = tuple(self.msgs.keys())

        for msgtype, handler in self.msgs.items():
            self.con.register(handler, msgtype)

        self.con.connect()

    def watcher(self, msg):
        if isinstance(msg, ib.opt.message.error):
            if msg.errorCode > 2000:  # informative message
                print('-' * 10, msg)

        elif not isinstance(msg, self.skipmsgs):
            print('-' * 10, msg)

    def errors(self, msg):
        if msg.id is None:  # something is very wrong in the connection to tws
            self.q.put((True, -1, 'Lost Connection to TWS'))
        elif msg.errorCode < 1000:
            self.q.put((True, msg.errorCode, msg.errorMsg))

    def contractDetailsHandler(self, msg):
        if isinstance(msg, ib.opt.message.contractDetailsEnd):
            self.q.put((False, msg.reqId, msg))
        else:
            self.q.put((False, msg.reqId, msg.contractDetails))

    def get_contract_details(self, symbol, sectype, exch='SMART', curr='USD'):
        contract = ib.ext.Contract.Contract()
        contract.m_symbol = symbol
        contract.m_exchange = exch
        contract.m_currency = curr
        contract.m_secType = sectype

        self.con.reqContractDetails(1, contract)

        cdetails = list()
        while True:
            try:
                err, mid, msg = self.q.get(block=True, timeout=self.timeout)
            except queue.Empty:
                err, mid, msg = True, -1, "Timeout receiving information"
                break

            if isinstance(msg, ib.opt.message.contractDetailsEnd):
                mid, msg = None, None
                break

            cdetails.append(msg)  # must be contractDetails

        # return list of contract details, followed by:
        #   last return code (False means no error / True Error)
        #   last error code or None if no error
        #   last error message or None if no error
        # last error message

        return cdetails, err, mid, msg


ibm = IbManager(clientId=5001)

cs = (
    ('ES', 'FUT', 'GLOBEX')
)

for c in cs:
    cdetails, err, errid, errmsg = ibm.get_contract_details(*c)

    if err:
        print('Last Error %d: %s' % (errid, errmsg))

    print('-' * 50)
    print('-- ', c)
    for cdetail in cdetails:
        # m_summary is the contract in details
        print('Expiry:', cdetail.m_summary.m_expiry)


sys.exit(0)  # Ensure ib thread is terminated