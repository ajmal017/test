import pandas as pd
import os, csv
from pathlib import Path
import argparse, datetime
import re


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except Exception:
        print("Unable to make directory %s" % directory)
    return True


def read_trades(file):
    """
    Read the trades.csv
    :param file: Filename
    :return: dataframe
    """
    columns = ['ID','TRADE']
    if not (os.path.exists(file)):
        msg = "Trades file not found."
        raise ValueError(msg)
    with open(file) as f:
        csvreader = csv.reader(f)

        for row in csvreader:
            trd = trade(row)


    return None

class trade():

    def __init__(self, trade_row=None):
        self.description = trade_row[1].split()
        self.id = trade_row[0]
        self.trade_type = self.description[0]
        self.qty = self.description[1]
        self.



class Trade():

    def __init__(self, each_line):
        self.execution_date = each_line[0]
        self.exection_time = each_line[1]
        self.type = each_line[2]
        self.trade_id = each_line[3]
        self.ticker = each_line[4].split()[2]
        self.execution_price = each_line[4].split()[3].split('@')[1]




class Statement():

    _date_format = '%m/%d/%y'

    def __init__(self, delta=None, ticker='SPX', start_date=None, end_date=None):
        self.delta = delta
        self.ticker = ticker
        self.today = valid_date(datetime.datetime.today().strftime(self._date_format))
        if end_date is None:
            self.end_date = self.today
        else:
            self.end_date = end_date

        if start_date is None:
            self.start_date = valid_date(datetime.datetime.today().replace(day=1))
        else:
            self.start_date = start_date
        print('Start Date: ', self.start_date, 'End Date: ', self.end_date)
        self.home = str(Path.home())
        self.date_format = "2019-05-11"
        self.directory = self.home + "/Documents/projects/test/tda/statements/"
        self.ensure_dir(self.directory)
        self.file = self.directory + "%s-AccountStatement.csv" % self.date_format
        if not (os.path.exists(self.file)):
            print("Statement file not found.")
            exit(0)

        self.modified_file_directory = self.directory + "/modified/"
        self.ensure_dir(self.modified_file_directory)
        self.cash_balance_file = self.modified_file_directory + \
                        "%s-cash_balance_modified.csv" % self.date_format
        self.trade_history_file = self.modified_file_directory + "%s-trade_history.csv" % self.date_format
        self.create_cash_balance_file(self.file, self.cash_balance_file)
        self.create_trade_history_file(self.file, self.trade_history_file)



    def ensure_dir(self, file_path):
        directory = os.path.dirname(file_path)
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except Exception:
            print("Unable to make directory %s" % directory)
        return True




    def create_cash_balance_file(self, infile, cash_balance_file):
        """
        Create the Modified statement file that contains only the Cash balance
        history
        :param infile: Main Statement
        :param modified_file: Modified Statement
        :return: None
        """
        with open(infile) as input, open(cash_balance_file, 'w') as output :
            writer = csv.writer(output)
            copy = False
            for row in csv.reader(input):
                if any('Cash Balance' in s for s in row):
                    copy = True
                    continue
                elif any('TOTAL' in s for s in row):
                    copy = False
                    continue
                elif copy:
                    writer.writerow(row)

        return None

    def create_trade_history_file(self, infile, trade_history_file):
        """
        Create the Modified trade history file
        :param infile: Main Statement
        :param modified_file: Modified Trade History
        :return: None
        """
        with open(infile) as input, open(trade_history_file, 'w') as output :
            writer = csv.writer(output)
            copy = False
            for row in csv.reader(input):
                if any('Account Trade History' in s for s in row):
                    copy = True
                    continue
                elif any('Options' in s for s in row):
                    copy = False
                    continue
                elif copy:
                    writer.writerow(row)

        return None

    def read_trade_history(self):
        columns = ['_','ExecTime','Spread','Side','Qty','Pos Effect','Symbol',
                   'Exp','Strike','Type','Price','Net Price','Order Type']

        parse_dates = ['ExecTime']
        df = pd.read_csv(self.trade_history_file, skiprows=1,delimiter=',',names=columns, parse_dates=parse_dates)
        df.ExecTime = pd.to_datetime(df.ExecTime)
        mask = (df.ExecTime >= self.start_date) & \
               (df.ExecTime <= self.end_date) & (df.Symbol == self.ticker)

        return df.loc[mask]

    def read_cash_balance(self):

        header = ['DATE','TIME','TYPE','REF #','DESCRIPTION',
                  'Misc Fees','Commissions & Fees','AMOUNT','BALANCE']
        parse_dates = ['DATE']
        df = pd.read_csv(self.cash_balance_file, skiprows=1,delimiter=',',names=header, parse_dates=parse_dates)
        df.DESCRIPTION = df.DESCRIPTION.str.strip()
        df.DATE = pd.to_datetime(df.DATE)
        mask = (df.DATE > self.start_date) & \
               (df.DATE < self.end_date) & \
               (df.TYPE == 'TRD')
        #mask = df.TYPE == 'TRD'
        return df.loc[mask]

    def print_cash_balance_file(self):
        """
        Print the cash balance file
        :return: None
        """
        with open(self.cash_balance_file) as f:
            csvreader = csv.reader(f)
            next(csvreader)
            for line in csvreader:
                if any(line):
                    _d = valid_date(line[0])
                    if _d >= self.start_date:
                        if line[2] == 'TRD':
                            if re.search(self.ticker, line[3]):
                                trade = Trade(line)
                                print(trade.ticker)
        return None

def valid_date(s):
    try:
        return datetime.datetime.strptime(s, '%m/%d/%y')
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def convert_date(s):
    try:
        return datetime.date.strftime(s, '%#m/%#d/%y')
    except ValueError:
        msg = "Unable to convert date: %s" % s
        raise argparse.ArgumentTypeError(msg)



def main(file):
    parser = argparse.ArgumentParser(description='TDA Trade History')
    parser.add_argument('-s', '--ticker', help='Stock symbol', required=False, default='NKD')
    parser.add_argument('-d', '--delta', help='Delta in Days', required=False, default=15)
    parser.add_argument('-sdate', '--sdate', help='Start Date', required=False, default='5/3/19', type=valid_date)
    parser.add_argument('-edate', '--edate', help='End Date', required=False, default='5/10/19', type=valid_date)
    args = vars(parser.parse_args())

    # Convert start & end date
    sDate = args['sdate']
    eDate = args['edate']
    # Initialize
    print('Fetching Last %s days of trade history for stock: %s' % (args['delta'], args['ticker']))

    #st = Statement(end_date=eDate,start_date=sDate)
    trd = trade(trade_df=read_trades(file=file))


    #st.print_cash_balance_file()
    #df = st.read_cash_balance()
    #df = st.read_trade_history()
    #print(df.to_string())




if(__name__ == "__main__"):
    directory = str(Path.home()) + "/Documents/projects/test/tda/statements/"
    ensure_dir(directory)
    file = directory + "trades.csv"
    main(file)