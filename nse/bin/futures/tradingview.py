import sys
import utils
import logging
import pairTrader
import csv
import pandas as pd
import os
import datetime
import numpy as np
import argparse

_const=utils.constants()


def initialize_logging(args):
    # Initialize Logging
    logger=logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # create a file handler
    _dir=_const.log_location + _const.timestr
    logname=_dir + '/' + _const.timestr + '.log'
    if not os.path.isdir(_dir):
        os.makedirs(_dir)
    # raise exception('Error in creating directory: %s' %(constants.log_location+constants.timestr))
    handler=logging.FileHandler(logname)
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    logger.info("Running Linear Regression")


directory='/home/abhishek/Downloads/'
header=['time', 'open', 'high', 'low', 'close', 'MA', 'MA1', 'Histogram', 'MACD', 'Signal']


def usfutures(basket, priceType, filename):
    """
    Convert the basket of US futures csv dataframe to a single dataframe in
    required format:
    <date.index Stock1 Stock2 Stock3>
    :param basket: Basket of US futures names
    :param filename: target file name
    :return: dataframe pandas
    """
    for k, v in enumerate(basket):
        inputFilename=directory + v.upper() + '.csv'
        if not os.path.isfile(inputFilename):
            print('File %s not present. Please download' % inputFilename)
            exit(0)

    inputFilename=directory + basket[0] + '.csv'
    firstStock=pd.read_csv(inputFilename, names=header, skiprows=1)
    print('Read successful: %s' % inputFilename)
    for i in range(1, len(basket)):
        _=directory + basket[i].upper() + '.csv'
        dfstock=pd.read_csv(_, names=header, skiprows=1)
        print('Read successful: %s' % _)
        if i == 1:
            data=pd.concat([firstStock[priceType].rename(basket[0]),
                            dfstock[priceType].rename(basket[i])], axis=1)
        else:
            data=pd.concat([data, dfstock[priceType].rename(basket[i])], axis=1)

    data.replace([np.inf, -np.inf], np.nan).dropna()
    data.to_csv(directory+filename)

    return data


def main():
    parser=argparse.ArgumentParser(description='Pairs strategy for ES and 6E')
    parser.add_argument('-y', '--ystock', help='First stock/futures symbol', default='ES')
    parser.add_argument('-x', '--xstock', help='Second stock/futures symbol', default='6E')
    args=vars(parser.parse_args())

    initialize_logging(args)

    # Initialize
    eTime=datetime.date.today()
    basket=['6A', '6E']

    name='indices'
    data=usfutures(basket, priceType='low', filename='consolidated.csv')

    if not pairTrader.LinearRegression_MODEL(data=data, filename='consolidated.csv'):
        print('Unable to execute Linear regression.')


if __name__ == '__main__':
    main()
