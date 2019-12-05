import numpy as np
import time
from statsmodels import regression
import statsmodels.api as sm
import matplotlib.pyplot as plt
import math
import pandas as pd
from statsmodels.tsa.stattools import coint
import nsepy
import os, sys
from utils import constants
from termcolor import colored
import datetime
# import nsequoter
import utils

# from colorama import init
# init()

##Reference:
## https://stackoverflow.com/questions/32101233/appending-predicted-values-and-residuals-to-pandas-dataframe
## Quantopian Lecture: https://www.quantopian.com/posts/quantopian-lecture-series-linear-regression
# location = "/Users/abhishek.chaturvedi/Downloads/Rough/projects/test/data/"
# directory_name = location+timestr+'/'
#
# Standard Error of Intercept : The variance of the intercept
# Standard Error : The variance of the residuals.
#    Error Ratio = Standard Error of Intercept / Standard Error

location = constants.location
timestr = constants.timestr
directory_name = constants.directory_name


def zscore(series):
    return (series - series.mean()) / np.std(series)


def LinearRegression_MODEL(data, filename):
    # Run Linear regression on all the possible pairs in basket and create a csv file
    model = pairTrader(data=data, filename=filename)
    # Run regression on all the downloaded pairs in basket
    # Creates QUALIFIED_DF
    file_name, qualified_df = model.LRegression_allPairs()
    # Filter the above csv file and only show qualifying trades
    if not model.LRegression_qualifiedPairs(filename=file_name,
                                            qualified_df=qualified_df):
        print("Unable to execute qualified pairs")
        return False

    return True


def usfutures(basket, filename):
    ## Convert the basket stocks individual frames to a single dataframe in
    ## format: <date.index Stock1 Stock2 Stock3>
    ##          data       'price' 'price' 'price'
    comment = 'D'
    timestr = time.strftime("%m-%d-%Y")
    columns = ['Time', 'Open', 'High', 'Low', 'Last', 'Change', 'Volume', 'Open Interest']
    for k, v in enumerate(basket):
        name = directory_name + v.lower() + '_price-history-%s.csv' % timestr
        if not os.path.isfile(name):
            print('File %s not present. Please download.' % name)
            exit(0)

    name = directory_name + basket[0] + '_price-history-%s.csv' % timestr
    first_stock = pd.read_csv(name, names=columns, skiprows=1, comment=comment)
    print('Read successful: %s' % name)
    for i in range(1, len(basket)):
        _ = directory_name + basket[i].lower() + '_price-history-%s.csv' % timestr
        dfstock = pd.read_csv(_, names=columns, skiprows=1, comment=comment)
        print('Read successful: %s' % _)
        if i == 1:
            data = pd.concat([first_stock['Last'].rename(basket[0]),
                              dfstock['Last'].rename(basket[i])],
                             axis=1)
        else:
            data = pd.concat([data, dfstock['Last'].rename(basket[i])],
                             axis=1)

    data.replace([np.inf, -np.inf], np.nan).dropna()
    # data.sort_values(by=['Time'], ascending=False)
    create_file_from_df(fName=filename, df=data)

    return data


class pull():
    # Class for pulling data
    def __init__(self, sTime, eTime, basket, filename, constants):
        self.sTime = sTime
        self.eTime = eTime
        self.basket = basket
        self.filename = filename
        self.constants = constants
        if not self.basket:
            print('Invalid Stock basket provided')
            exit(0)

    def pullData(self):
        """
        :return: Dataframe
        """
        """Pull data from NSEPY HISTORY FUNCTION"""
        # IF condition for BANKNIFTY index=True flag while
        # Pulling first_stock
        index = True if self.basket[0] in constants.index else False
        first_stock = nsepy.get_history(symbol=self.basket[0].upper(),
                                        start=self.sTime, end=self.eTime, index=index)
        # Pull data for the rest of the basket stocks
        for i in range(1, len(self.basket)):
            index = True if self.basket[i] in constants.index else False
            dfstock = nsepy.get_history(symbol=self.basket[i], start=self.sTime, end=self.eTime, index=index)
            if i == 1:
                data = pd.concat([first_stock['Close'].rename(self.basket[0]),
                                  dfstock['Close'].rename(self.basket[i])],
                                 axis=1)
            else:
                data = pd.concat([data, dfstock['Close'].rename(self.basket[i])],
                                 axis=1)

        # Set Date as index
        # data.set_index('Date', inplace=True)

        data.replace([np.inf, -np.inf], np.nan).dropna()
        data.sort_index(inplace=True, ascending=True)
        print(data.head())
        # data.sort_values(by=['Date'], ascending=False)
        # Create CSV from dataframe
        create_file_from_df(fName=self.filename, df=data)

        return data

    def pullindex(self):

        # merge = pd.DataFrame(columns=['Date'])
        first_stock = nsepy.get_history(symbol=self.basket[0].upper(), start=self.sTime, end=self.eTime, index=True)
        for i in range(1, len(self.basket)):
            dfstock = nsepy.get_history(symbol=self.basket[i], start=self.sTime, end=self.eTime, index=True)

            if i == 1:
                data = pd.concat([first_stock['Close'].rename(self.basket[0]),
                                  dfstock['Close'].rename(self.basket[i])],
                                 axis=1)
            else:
                data = pd.concat([data, dfstock['Close'].rename(self.basket[i])],
                                 axis=1)

        # Set Date as index
        # data.set_index('Date', inplace=True)
        data.replace([np.inf, -np.inf], np.nan).dropna()
        data.sort_values(by=['Date'], ascending=False)
        # Create CSV from dataframe
        create_file_from_df(fName=self.filename, df=data)

        return data


class pairTrader():
    # Pair Trader class
    def __init__(self, data=None, stockY=None, stockX=None, sTime=None,
                 eTime=None, basket=None, filename=None,
                 qualified_df=None):
        self.data = data
        self.stockY = stockY
        self.stockX = stockX
        self.sTime = sTime
        self.eTime = eTime
        self.basket = basket
        self.filename = filename
        self.qualified_df = qualified_df

    def create_file_from_df(self, fName, df):
        """
        Create a csv file from dataframe
        :param fName: Filename
        :param df: dataframe
        :return: None
        """
        try:
            df.to_csv('%s' % fName)
        except Exception as e:
            print(e)
        print('Created CSV Data file : %s' % fName)
        return None

    def linreg(self, y, x, inverse=False):
        # Running the linear regression
        X = sm.add_constant(x)
        _model = regression.linear_model.OLS(y, X).fit()
        # a = model.params[0]
        # b = model.params[1]
        X = X[:, 1]

        """ Plot
        # Return summary of the regression and plot results
        X2 = np.linspace(X.min(), X.max(), 100)
        Y_hat = X2 * b + a
        plt.scatter(X, Y, alpha=0.3) # Plot the raw data
        plt.plot(X2, Y_hat, 'r', alpha=0.9);  # Add the regression line, colored in red
        plt.xlabel('X Value')
        plt.ylabel('Y Value')
        """
        return _model

    def get_std_err_intercept(self, model):
        # Variance of Intercept
        return model.bse[0]

    def get_std_err(self, model):
        # Variance of Residuals
        return model.resid.std()

    def get_std_err_ratio(self, model):
        ##Choose the least std error ratio
        return self.get_std_err_intercept(model) / self.get_std_err(model)

    def get_alpha(self, model):
        # Coefficient or Intercept or ALPHA
        return '%.2f' % model.params[0]

    def get_beta(self, model):
        # Beta OR Slope
        return '%.2f' % model.params[1]

    def get_pvalue(self, model):
        return '%.4f' % model.f_pvalue

    def get_current_std_err(self, model):
        """
        Returns the Z-Score
        """
        return '%.2f' % (model.resid[-1] / self.get_std_err(model))

    def get_alpha_price_ratio(self, model, price):
        # Return the Alpha : Price ratio
        alpha = self.get_alpha(model)
        return 100 * float(alpha) / float(price)

    def print_model_info(self, model):
        print(model.summary())
        print('Standard error of Intercept', self.get_std_err_intercept(model))
        print('\nStandard error', self.get_std_err(model))
        print('\nStandard Error Ratio', self.get_std_err_ratio(model))
        print('\nAlpha', self.get_alpha(model))
        print('\nBeta', self.get_beta(model))
        print('\nPValue', self.get_pvalue(model))
        print('\nCurrent Std Error (Z-Score):', self.get_current_std_err(model))

    def find_cointegrated_pairs(self, data, pfilter):
        n = data.shape[1]
        score_matrix = np.zeros((n, n))
        pvalue_matrix = np.ones((n, n))
        keys = data.keys()
        pairs = []

        for i in range(n):
            for j in range(i + 1, n):
                S1 = data[keys[i]]
                S2 = data[keys[j]]
                result = coint(S1, S2)
                score = result[0]
                pvalue = result[1]
                score_matrix[i, j] = score
                pvalue_matrix[i, j] = pvalue
                if pvalue < pfilter:
                    print('pvalue', pvalue)
                    pairs.append((keys[i], keys[j]))
        # return_list = [score_matrix, pvalue_matrix, pairs]
        return score_matrix, pvalue_matrix, pairs

    def set_values(self, model, Y, X, df):
        ## Create an empty dataframe and then insert the model values to it
        ## Returns True on successfull work

        rows_list = []
        rows_list.append(Y)
        rows_list.append(X)
        rows_list.append(self.get_pvalue(model))
        rows_list.append(self.get_beta(model))
        rows_list.append('%.2f' % self.get_std_err_ratio(model))
        rows_list.append(self.get_alpha(model))
        rows_list.append(self.get_current_std_err(model))
        rows_list.append(self.get_alpha_price_ratio(model, df[Y].iat[-1]))
        # rows_list.append(df[Y].iat[-1])

        return rows_list

    def LRegression_allPairs(self):
        """
        input: dataframe containing a basket of stock closing prices
        :return Nothing, just create the file
        ## Perform linear regression on all the possible pairs in the provided basket of stocks
        ## Store their OLS model results and write them out to a csv file
        """
        #Get the Linear regression header from constants
        columns = constants.header
        qualified_df = pd.DataFrame(columns=columns)
        # qualified_df = pd.DataFrame(columns=columns)
        data = self.data.dropna()
        print(data.tail())
        n = data.shape[1]
        keys = data.keys()

        # Loop through the merged dataframe and run LRegression on each pair
        # First A as Y and B as X, then A as X and B as Y
        # Pick only the pair series which has std_err_ratio least between the two combinations
        # Create the CSV file allPairs_<filename>.csv
        for i in range(n):
            Y = np.asarray(data[keys[i]])
            for j in range(i + 1, n):
                X = np.asarray(data[keys[j]])
                model = self.linreg(y=Y, x=X)
                inverse_model = self.linreg(y=X, x=Y)
                """
                print("YStock %s ======== XStock %s" % (keys[i], keys[j]))
                print(self.print_model_info(model))
                print("+++++")
                print("YStock %s ======== XStock %s" % (keys[j], keys[i]))
                print(self.print_model_info(inverse_model))
                """
                """
                if self.get_std_err_ratio(model) < self.get_std_err_ratio(inverse_model):
                    print('\tChoosing YStock : %s XStock: %s' % (keys[i], keys[j]))
                    qualified_df.loc[len(qualified_df)] = self.set_values(model, Y=keys[i], X=keys[j], df=data)
                else:
                    print('\tChoosing YStock : %s XStock: %s' % (keys[j], keys[i]))
                    qualified_df.loc[len(qualified_df)] = self.set_values(inverse_model, Y=keys[j], X=keys[i], df=data)
                """
                print('\tChoosing YStock : %s XStock: %s' % (keys[i], keys[j]))
                qualified_df.loc[len(qualified_df)] = self.set_values(model, Y=keys[i], X=keys[j], df=data)
                print('\tChoosing YStock : %s XStock: %s' % (keys[j], keys[i]))
                qualified_df.loc[len(qualified_df)] = self.set_values(inverse_model, Y=keys[j], X=keys[i], df=data)

        print("\nAll Pairs Data:")
        print(qualified_df)

        file_name = directory_name + 'allPairs_' + self.filename
        self.create_file_from_df(fName=file_name, df=qualified_df)
        return file_name, qualified_df

    def LRegression_qualifiedPairs_backup(self, data, pairs, filename):
        """
        Perform linear regression on only the selected pairs after COINT
        Store the OLS model results in a csv file
        Selection Criteria:
            1. Compare the STD_ERRROR Ratio of Intercept / Std. Err of residuals and select the YStock which has this ratio minimum
            2. Filter for only those Y:X stock pairs which have the std_err (variance of current residuals) above or below the 1SD/2SD
        """

        header = ['YStock', 'XStock', 'PValue', 'Beta', 'STD_ERR_Ratio', 'Alpha', 'Current_STD_Error']
        qualified_df = pd.DataFrame(columns=header)
        sd_matrix = [-3.0, -2.0, -1.0, 1.0, 2.0, 3.0]
        data = data.dropna
        keys = data.keys()
        for k, v in pairs:
            Y = np.asarray(data[k])
            X = np.asarray(data[v])
            model = self.linreg(Y=Y, X=X)
            inverse_model = self.linreg(Y=X, X=Y)

            if self.get_std_err_ratio(model) < self.get_std_err_ratio(inverse_model):
                ## Condition for checking which stock will be Y and which will be X
                ## Then choose the type of trade depending upon the current std_err value
                # print('\tChoosing YStock : %s XStock: %s' % (keys[i],keys[j])
                if self.get_current_std_err(model) <= sd_matrix[1]:
                    qualified_df.loc[len(qualified_df)] = self.set_values(model, Y=k, X=v)
                    print('Qualified Trade: YStock = %s and XStock = %s' % (k, v))
                    print('Buy : %s Sell %s' % (k, v))
                if self.get_current_std_err(model) >= sd_matrix[4]:
                    qualified_df.loc[len(qualified_df)] = self.set_values(model, Y=k, X=v)
                    print('Qualified Trade: YStock = %s and XStock = %s' % (k, v))
                    print('Sell : %s Buy %s' % (k, v))

            else:
                # print('\tChoosing YStock : %s XStock: %s' % (keys[j], keys[i])
                if self.get_current_std_err(inverse_model) <= sd_matrix[1]:
                    qualified_df.loc[len(qualified_df)] = self.set_values(inverse_model, Y=v, X=k)
                    print('Qualified Trade: YStock = %s and XStock = %s' % (v, k))
                    print('Buy : %s Sell %s' % (v, k))
                if self.get_current_std_err(inverse_model) >= sd_matrix[4]:
                    qualified_df.loc[len(qualified_df)] = self.set_values(inverse_model, Y=k, X=v)
                    print('Qualified Trade: YStock = %s and XStock = %s' % (v, k))
                    print('Buy : %s Sell %s' % (v, k))

        name = directory_name + 'qualified_' + filename
        if not qualified_df.empty:
            qualified_df.to_csv(name)
            print('Created qualified pair trader file: %s' % (name))
        else:
            print('No qualified pairs identified.')
        return None

    def LRegression_qualifiedPairs(self, filename, qualified_df):
        """
        Perform linear regression on only the selected pairs after COINT
        Store the OLS model results in a csv file
        Selection Criteria:
            1. Compare the STD_ERRROR Ratio of Intercept / Std. Err of residuals and select the YStock which has this ratio minimum
            2. Filter for only those Y:X stock pairs which have the std_err (variance of current residuals) above or below the 1SD/2SD
        """

        columns = constants.header
        #qualified_df = pd.DataFrame(columns=columns)
        sd_matrix = [-3.0, -2.5, -1.0, 1.0, 2.5, 3.0]
        keys = self.data.keys()
        n = self.data.shape[1]
        print('## Trying to find pairs qualifying for a trade ##')
        """try:
            data = pd.read_csv(self.filename,skiprows=1,names=columns)
            print('Successfully read file: %s' % self.filename)
        except Exception as e:
            print('Unable to read file: %s' % self.filename)
            print(e)
        """
        data = qualified_df
        print("EXITING FORCEFULLY")
        sys.exit(1)
        pvalue_boolean = data.PValue <= constants.pfilter
        data = qualified_df[pvalue_boolean]
        less2SD = (data['Close_STD_Error'] <= -2.5) & (data['Close_STD_Error'] >= -3.0) & (data['Beta'] > 0.0)
        greater2SD = (data['Close_STD_Error'] >= 2.5) & (data['Close_STD_Error'] <= 3.0) & (data['Beta'] > 0.0)
        less3SD = (data['Close_STD_Error'] <= -3.0) & (data['Beta'] > 0.0)
        greater3SD = (data['Close_STD_Error'] >= 3.0) & (data['Beta'] > 0.0)

        frame_over2SD = data[greater2SD]
        frame_less2SD = data[less2SD]
        frame_over3SD = data[greater3SD]
        frame_less3SD = data[less3SD]

        filename = self.filename.split('.csv')[0]
        """dir+banknifty.csv split to dir+banknifty"""
        print(colored('## Qualified trades ##', 'red'))
        name = filename + '_qualified_over2SD.csv'
        if not frame_over2SD.empty:
            self.create_file_from_df(fName=name, df=frame_over2SD)
            print(colored('INFO: Over 2SD', 'red'))
            print(colored(frame_over2SD, 'green'))
            print(colored('Created qualified pair trader file: %s\n' % name, 'blue'))
        name = filename + '_qualified_less2SD.csv'
        if not frame_less2SD.empty:
            print(colored('INFO: Less than 2SD', 'red'))
            self.create_file_from_df(fName=name, df=frame_less2SD)
            print(colored(frame_less2SD, 'green'))
            print(colored('Created qualified pair trader file: %s\n' % name, 'blue'))
        name = filename + '_qualified_over3SD.csv'
        if not frame_over3SD.empty:
            print(colored('INFO: Over 3SD', 'red'))
            self.create_file_from_df(name, frame_over3SD)
            print(colored(frame_over3SD, 'green'))
            print(colored('Created qualified pair trader file: %s\n' % name, 'blue'))
        name = filename + '_qualified_less3SD.csv'
        if not frame_less3SD.empty:
            print(colored('INFO: Less than 3SD', 'red'))
            self.create_file_from_df(name, frame_less3SD)
            print(colored(frame_less3SD, 'green'))
            print(colored('Created qualified pair trader file: %s\n' % name, 'blue'))

        return True

    def model_current_std_err(self, data, YStock, XStock, search_string='lastPrice'):

        columns = ['YStock', 'XStock']

        u = utils.Utils()
        u._codes['NIFTY'] = 'Nifty Index'
        u._codes['BANKNIFTY'] = 'Bank Nifty Index'

        # Get current date
        current_date = datetime.date.today()
        # current_data = pd.read_csv(constants.current_filename,names=columns)

        try:
            # Get current quote for YStock
            if YStock in constants.index:
                ystock_price = u.get_quote(YStock, cont='FUTIDX', mon=constants.expiry_month,
                                           search_string=search_string)
            else:
                ystock_price = nsequoter.get_equity_quote(YStock)
            # ystock_price = nsequoter.get_futures_quote(YStock, current_date.strftime("%b"))
            # Get current quote for YStock
            if XStock in constants.index:
                xstock_price = u.get_quote(XStock, cont='FUTIDX', mon=constants.expiry_month,
                                           search_string=search_string)
            else:
                xstock_price = nsequoter.get_equity_quote(XStock)
            # xstock_price = nsequoter.get_futures_quote(XStock, current_date.strftime("%b"))
            current_data = pd.DataFrame([[0, 1], [ystock_price, xstock_price]], columns=columns)
            print(colored('Current %s stock price: %s' % (YStock, ystock_price), 'cyan'))
            print(colored('Current %s stock price: %s' % (XStock, xstock_price), 'cyan'))
            # Create an NP array from dataframe column containing the stock price history
            # Y and X stock
            Y = np.asarray(data[YStock])
            X = np.asarray(data[XStock])
            # Append the current respective stock prices to the above arrays
            _y = np.append(Y, current_data.YStock)
            _x = np.append(X, current_data.XStock)
            model = self.linreg(Y=_y, X=_x)
            print(colored('Model\'s current std error: %s\n' % self.get_current_std_err(model), 'yellow'))

        except Exception as e:
            print(colored('Unable to fetch %s futures price' % search_string, 'red'))
            print(e)

        pass

    def model_open_std_err(self, data, YStock, XStock):
        columns = ['YStock', 'XStock']
        try:
            u = utils.Utils()
            # Get current quote for YStock

            if YStock in constants.index:
                ystock_open = u.get_open(YStock, cont='FUTIDX', mon=constants.expiry_month)
            else:
                ystock_open = u.get_open(YStock)
            # Get current quote for YStock
            if XStock in constants.index:
                xstock_open = u.get_open(XStock, cont='FUTIDX', mon=constants.expiry_month)
            else:
                xstock_open = u.get_open(XStock)
            current_data = pd.DataFrame([[0, 1], [ystock_open, xstock_open]], columns=columns)
            print(colored('Open %s stock price: %s' % (YStock, ystock_open), 'cyan'))
            print(colored('Open %s stock price: %s' % (XStock, xstock_open), 'cyan'))
            # Create an NP array from dataframe column containing the stock price history
            # Y and X stock
            Y = np.asarray(data[YStock])
            X = np.asarray(data[XStock])
            # Append the current respective stock prices to the above arrays
            _y = np.append(Y, current_data.YStock)
            _x = np.append(X, current_data.XStock)
            model = self.linreg(Y=_y, X=_x)
            print(colored('Model\'s Open std error: %s\n' % self.get_current_std_err(model), 'yellow'))

        except Exception as e:
            print(colored('Unable to fetch open futures price', 'red'))
            print(e)

        return None
