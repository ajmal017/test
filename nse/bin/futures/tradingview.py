import utils
import logging
import pairTrader
import pandas as pd
import os
import datetime
import numpy as np
import argparse

_const = utils.constants()


def initialize_logging(args):
    # Initialize Logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # create a file handler
    _dir = _const.log_location + _const.timestr
    logname = _dir + '/' + _const.timestr + '.log'
    if not os.path.isdir(_dir):
        os.makedirs(_dir)
    # raise exception('Error in creating directory: %s' %(constants.log_location+constants.timestr))
    handler = logging.FileHandler(logname)
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    logger.info("Running Linear Regression")


directory = '/home/abhishek/Downloads/tradingview/'
tradingView_header = ['time', 'open', 'high', 'low', 'close', 'MA', 'MA1', 'Histogram', 'MACD', 'Signal']


def usfutures(basket, priceType, filename, skipfoot=0):
    """
    Convert the basket of US futures csv dataframe to a single dataframe in
    required format:
    <date.index Stock1 Stock2 Stock3>
    :param basket: Basket of US futures names
    :param filename: target file name
    :return: dataframe pandas
    """
    for k, v in enumerate(basket):
        inputFilename = directory + v.upper() + '.csv'
        if not os.path.isfile(inputFilename):
            print('File %s not present. Please download' % inputFilename)
            exit(0)

    inputFilename = directory + basket[0] + '.csv'
    firstStock = pd.read_csv(inputFilename, names=tradingView_header, skiprows=1,
                             skipfooter=skipfoot, engine='python')
    print('Read successful: %s' % inputFilename)
    for i in range(1, len(basket)):
        _ = directory + basket[i].upper() + '.csv'
        dfstock = pd.read_csv(_, names=tradingView_header, skiprows=1)
        print('Read successful: %s' % _)
        if i == 1:
            data = pd.concat([firstStock[priceType].rename(basket[0]),
                              dfstock[priceType].rename(basket[i])], axis=1)
        else:
            data = pd.concat([data, dfstock[priceType].rename(basket[i])], axis=1)

    data.replace([np.inf, -np.inf], np.nan).dropna()
    data.to_csv(directory + filename)

    return data


def rename_files():
    """
    Rename the Tradingview downloaded files
    """
    extension = '.csv'
    for infile in os.listdir(directory):
        if ',' in infile:
            os.rename(directory + infile, directory + infile.split(',')[0].split('_')[1] + extension)

    return True


def main():
    parser = argparse.ArgumentParser(description='Pairs strategy for ES and 6E')
    parser.add_argument('-y', '--ystock', help='First stock/futures symbol', default='6A')
    parser.add_argument('-x', '--xstock', help='Second stock/futures symbol', default='6E')
    parser.add_argument('-type', '--pricetype', help='Price type open|high|low|close', default='close')
    parser.add_argument('-skip', '--skip', help='Number of rows to skip from bottom', default=0)
    args = vars(parser.parse_args())

    initialize_logging(args)

    # Initialize
    eTime = datetime.date.today()
    basket = [args['ystock'], args['xstock']]  # , 'ES','NQ']
    # basket = ['CME_6AZ2019','CME_6EZ2019','CBOT_ZNZ2019','CME_6NZ2019','CME_MINI_MESZ2019',
    #          'COMEX_GCF2020','NSE_SBIN','NYMEX_CLF2020','NYMEX_MINI_QMF2020']
    currency_basket = ['CME_6AZ2019', 'CME_6EZ2019', 'CME_6NZ2019']
    consolidated_file_header = ['ind', basket[0], basket[1]]
    name = '-'.join(i for i in basket)
    filename = 'consolidated-%s.csv' % name

    rename_files()

    if os.path.isfile(directory + filename):
        # Re-read the consolidated csv if it already exists
        print('Data already downloaded in file: %s' % (directory + filename))
        try:
            data = pd.read_csv(directory + filename, skiprows=1, names=consolidated_file_header)
            print(data.tail())
            # Set Date as index
            data.set_index(consolidated_file_header[0], inplace=True)
            data.sort_values(by=[consolidated_file_header[0]], ascending=False)
        except Exception as e:
            print(e)
    else:
        # Prepare consolidated dataframe csv from downloaded data
        pass

    data = usfutures(basket, priceType=args['pricetype'].lower(), filename=filename,
                     skipfoot=int(args['skip']))

    if not pairTrader.LinearRegression_MODEL(data=data, filename=filename):
        print('Unable to execute Linear regression.')


if __name__ == '__main__':
    main()
