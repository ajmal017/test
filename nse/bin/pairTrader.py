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
from get_futures import constants
from termcolor import colored
import datetime
import nsequoter

##Reference:
## https://stackoverflow.com/questions/32101233/appending-predicted-values-and-residuals-to-pandas-dataframe
## Quantopian Lecture: https://www.quantopian.com/posts/quantopian-lecture-series-linear-regression
#location = "/Users/abhishek.chaturvedi/Downloads/Rough/projects/test/data/"
#directory_name = location+timestr+'/'

location = constants.location
timestr = constants.timestr
directory_name = constants.directory_name

def zscore(series):
    return (series - series.mean()) / np.std(series)


def create_file_from_df(fName, df):
    try:
        df.to_csv('%s' % fName)

    except Exception, e:
        print e

    print 'Created Merged Data file : %s' % fName
    return None

def usfutures(basket, filename):
    ## Convert the basket stocks individual frames to a single dataframe in
    ## format: <date.index Stock1 Stock2 Stock3>
    ##          data       'price' 'price' 'price'
    comment = 'D'
    timestr = time.strftime("%m-%d-%Y")
    columns = ['Time','Open','High','Low','Last','Change','Volume','Open Interest']
    for k,v in enumerate(basket):
        name = directory_name + v.lower() + '_price-history-%s.csv' % timestr
        if not os.path.isfile(name):
            print 'File %s not present. Please download.' % name
            exit(0)

    name = directory_name + basket[0] + '_price-history-%s.csv' % timestr
    first_stock = pd.read_csv(name, names=columns, skiprows=1,comment=comment)
    print 'Read successful: %s' % name
    for i in range(1,len(basket)):
        _ = directory_name + basket[i].lower() + '_price-history-%s.csv' % timestr
        dfstock = pd.read_csv(_, names=columns, skiprows=1,comment=comment)
        print 'Read successful: %s' % _
        if i == 1:
            data = pd.concat([first_stock['Last'].rename(basket[0]),
                              dfstock['Last'].rename(basket[i])],
                             axis=1)
        else:
            data = pd.concat([data, dfstock['Last'].rename(basket[i])],
                             axis=1)

    data.replace([np.inf, -np.inf], np.nan).dropna()
    #data.sort_values(by=['Time'], ascending=False)
    create_file_from_df(fName=filename, df=data)

    return data




def pullData(stockY=None, stockX=None, future=False, nifty=False, bnifty=False, sTime=None, eTime=None, basket=None
             , filename=None):
    if not basket:
        print 'Invalid Stock basket provided'
        exit(0)

    # merge = pd.DataFrame(columns=['Date'])
    if basket[0] == 'BANKNIFTY':
        first_stock = nsepy.get_history(symbol=basket[0], start=sTime, end=eTime,index=True,
                                    futures=True,expiry_date=constants.expiry_date)
    else:
        first_stock = nsepy.get_history(symbol=basket[0], start=sTime, end=eTime,
                                    futures=True, expiry_date=constants.expiry_date)

    for i in range(1, len(basket)):
        dfstock = nsepy.get_history(symbol=basket[i], start=sTime, end=eTime,
                                    futures=True,expiry_date=constants.expiry_date)

        if i == 1:
            data = pd.concat([first_stock['Close'].rename(basket[0]),
                              dfstock['Close'].rename(basket[i])],
                             axis=1)
        else:
            data = pd.concat([data, dfstock['Close'].rename(basket[i])],
                             axis=1)

    # Set Date as index
    # data.set_index('Date', inplace=True)
    data.replace([np.inf, -np.inf], np.nan).dropna()
    data.sort_values(by=['Date'], ascending=False)
    create_file_from_df(fName=filename, df=data)

    return data


def linreg(Y, X):
    # Running the linear regression
    X = sm.add_constant(X)
    model = regression.linear_model.OLS(Y, X).fit()
    #a = model.params[0]
    #b = model.params[1]
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
    return model

def get_std_err_intercept(model):
    return  model.bse[0]
def get_std_err(model):
    return model.resid.std()
def get_std_err_ratio(model):
    ##Choose the least std error ratio
    return get_std_err_intercept(model) / get_std_err(model)
def get_alpha(model):
    return '%.2f' % model.params[0]
def get_beta(model):
    return '%.2f' %model.params[1]
def get_pvalue(model):
    return '%.2f' % model.f_pvalue
def get_current_std_err(model):
    return '%.2f' %(model.resid[-1] / get_std_err(model))

def print_model_info(model):
    print model.summary()
    print 'Standard error of Intercept', get_std_err_intercept(model)
    print '\nStandard error', get_std_err(model)
    print '\nStandard Error Ratio', get_std_err_ratio(model)

    print '\nAlpha', get_alpha(model)
    print '\nBeta', get_beta(model)
    print '\nPValue', get_pvalue(model)
    print '\nCurrent Std Error:', get_current_std_err(model)

def find_cointegrated_pairs(data, pfilter):
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []

    for i in range(n):
        for j in range(i+1, n):
            S1 = data[keys[i]]
            S2 = data[keys[j]]
            result = coint(S1, S2)
            score = result[0]
            pvalue = result[1]
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < pfilter:
                print 'pvalue',pvalue
                pairs.append((keys[i], keys[j]))
    #return_list = [score_matrix, pvalue_matrix, pairs]
    return score_matrix, pvalue_matrix, pairs

def set_values(model, Y, X):
    ## Create an empty dataframe and then insert the model values to it
    ## Returns True on successfull work

    rows_list = []
    rows_list.append(Y)
    rows_list.append(X)
    rows_list.append(get_pvalue(model))
    rows_list.append(get_beta(model))
    rows_list.append('%.2f' % get_std_err_ratio(model))
    rows_list.append(get_alpha(model))
    rows_list.append(get_current_std_err(model))

    """
    running_df.YStock = Y
    running_df.XStock = X
    running_df.PValue = get_pvalue(model)
    running_df.Beta = get_beta(model)
    running_df.STD_ERR_Ratio = get_std_err_ratio(model)
    running_df.Alpha = get_alpha(model)
    running_df.Current_STD_Error = get_current_std_err(model)
    """


    return rows_list

def LRegression_allPairs(data, filename):
    """
    input: dataframe containing a basket of stock closing prices
    :return Nothing, just create the file
    ## Perform linear regression on all the possible pairs in the provided basket of stocks
    ## Store their OLS model results and write them out to a csv file
    """
    header = ['YStock', 'XStock', 'PValue', 'Beta', 'STD_ERR_Ratio', 'Alpha', 'Current_STD_Error']
    running_df = pd.DataFrame(columns=header)
    qualified_df = pd.DataFrame(columns=header)
    data = data.dropna()
    n = data.shape[1]

    keys = data.keys()

    for i in range(n):
        for j in range(i+1,n):
            Y = np.asarray(data[keys[i]])
            X = np.asarray(data[keys[j]])
            model = linreg(Y=Y, X=X)
            inverse_model = linreg(Y=X, X=Y)

            if get_std_err_ratio(model) < get_std_err_ratio(inverse_model):
                #print '\tChoosing YStock : %s XStock: %s' % (keys[i],keys[j])
                running_df.loc[len(running_df)] = set_values(model, Y=keys[i], X=keys[j])
            else:
                #print '\tChoosing YStock : %s XStock: %s' % (keys[j], keys[i])
                running_df.loc[len(running_df)] = set_values(inverse_model, Y=keys[j], X=keys[i])

    name = directory_name+'allPairs_'+filename
    running_df.to_csv(name)
    print '\nCreated All Pairs trader file: %s' % (name)
    return name

def LRegression_qualifiedPairs(data, pairs, filename):
    """
    Perform linear regression on only the selected pairs after COINT
    Store the OLS model results in a csv file
    Selection Criteria:
        1. Compare the STD_ERRROR Ratio of Intercept / Std. Err of residuals and select the YStock which has this ratio minimum
        2. Filter for only those Y:X stock pairs which have the std_err (variance of current residuals) above or below the 1SD/2SD
    """

    header = ['YStock', 'XStock', 'PValue', 'Beta', 'STD_ERR_Ratio', 'Alpha', 'Current_STD_Error']
    qualified_df = pd.DataFrame(columns=header)
    sd_matrix = [-3.0,-2.0,-1.0,1.0,2.0,3.0]
    data = data.dropna
    keys = data.keys()
    for k,v in pairs:
        Y = np.asarray(data[k])
        X = np.asarray(data[v])
        model = linreg(Y=Y, X=X)
        inverse_model = linreg(Y=X, X=Y)

        if get_std_err_ratio(model) < get_std_err_ratio(inverse_model):
            ## Condition for checking which stock will be Y and which will be X
            ## Then choose the type of trade depending upon the current std_err value
            #print '\tChoosing YStock : %s XStock: %s' % (keys[i],keys[j])
            if get_current_std_err(model) <= sd_matrix[1]:
                qualified_df.loc[len(qualified_df)] = set_values(model, Y=k, X=v)
                print 'Qualified Trade: YStock = %s and XStock = %s' % (k,v)
                print 'Buy : %s Sell %s' % (k,v)
            if get_current_std_err(model) >= sd_matrix[4]:
                qualified_df.loc[len(qualified_df)] = set_values(model, Y=k, X=v)
                print 'Qualified Trade: YStock = %s and XStock = %s' % (k,v)
                print 'Sell : %s Buy %s' % (k,v)

        else:
            #print '\tChoosing YStock : %s XStock: %s' % (keys[j], keys[i])
            if get_current_std_err(inverse_model) <= sd_matrix[1]:
                qualified_df.loc[len(qualified_df)] = set_values(inverse_model, Y=v, X=k)
                print 'Qualified Trade: YStock = %s and XStock = %s' % (v,k)
                print 'Buy : %s Sell %s' % (v,k)
            if get_current_std_err(inverse_model) >= sd_matrix[4]:
                qualified_df.loc[len(qualified_df)] = set_values(inverse_model, Y=k, X=v)
                print 'Qualified Trade: YStock = %s and XStock = %s' % (v, k)
                print 'Buy : %s Sell %s' % (v, k)

    name = directory_name+'qualified_'+filename
    if not qualified_df.empty:
        qualified_df.to_csv(name)
        print 'Created qualified pair trader file: %s' % (name)
    else:
        print 'No qualified pairs identified.'
    return None

def LRegression_qualifiedPairs1(data, filename):
    """
    Perform linear regression on only the selected pairs after COINT
    Store the OLS model results in a csv file
    Selection Criteria:
        1. Compare the STD_ERRROR Ratio of Intercept / Std. Err of residuals and select the YStock which has this ratio minimum
        2. Filter for only those Y:X stock pairs which have the std_err (variance of current residuals) above or below the 1SD/2SD
    """

    columns = ['YStock', 'XStock', 'PValue', 'Beta', 'STD_ERR_Ratio', 'Alpha', 'Current_STD_Error']
    qualified_df = pd.DataFrame(columns=columns)
    sd_matrix = [-3.0,-2.0,-1.0,1.0,2.0,3.0]
    keys = data.keys()
    n = data.shape[1]
    print '## Trying to find pairs qualifying for a trade ##'
    try:
        data = pd.read_csv(filename,skiprows=1,names=columns)
        print 'Successfully read file: %s' % filename
    except Exception,e:
        print 'Unable to read file: %s' % filename
        print e
    pvalue_boolean = data.PValue < 0.02
    data = data[pvalue_boolean]
    less2SD = (data['Current_STD_Error'] <= -2.0) & (data['Current_STD_Error'] >= -3.0) & (data['Beta'] > 0.0)
    greater2SD = (data['Current_STD_Error'] >= 2.0) & (data['Current_STD_Error'] <= 3.0) & (data['Beta'] > 0.0)
    less3SD = (data['Current_STD_Error'] <= -3.0) & (data['Beta'] > 0.0)
    greater3SD = (data['Current_STD_Error'] >= 3.0) & (data['Beta'] > 0.0)


    frame_over2SD = data[greater2SD]
    frame_less2SD = data[less2SD]
    frame_over3SD = data[greater3SD]
    frame_less3SD = data[less3SD]

    filename = filename.split('.csv')[0]

    print colored('## Qualified trades ##', 'red')
    name = filename + '_qualified_over2SD.csv'
    if not frame_over2SD.empty:
        frame_over2SD.to_csv(name)
        print colored('INFO: Over 2SD','red')
        print colored(frame_over2SD,'green')
        print colored('Created qualified pair trader file: %s\n' % (name),'blue')
    name = filename + '_qualified_less2SD.csv'
    if not frame_less2SD.empty:
        print colored('INFO: Less than 2SD', 'red')
        frame_less2SD.to_csv(name)
        print colored(frame_less2SD, 'green')
        print colored('Created qualified pair trader file: %s\n' % name,'blue')
    name = filename + '_qualified_over3SD.csv'
    if not frame_over3SD.empty:
        print colored('INFO: Over 3SD', 'red')
        frame_over3SD.to_csv(name)
        print colored(frame_over3SD, 'green')
        print colored('Created qualified pair trader file: %s\n' % name,'blue')
    name = filename + '_qualified_less3SD.csv'
    if not frame_less3SD.empty:
        print colored('INFO: Less than 3SD', 'red')
        frame_less3SD.to_csv(name)
        print colored(frame_less3SD, 'green')
        print colored('Created qualified pair trader file: %s\n' % name,'blue')


    return None

def model_current_std_err(data, YStock, XStock):

    columns = ['YStock', 'XStock']
    #Get current date
    current_date = datetime.date.today()
    #current_data = pd.read_csv(constants.current_filename,names=columns)

    try:
        #Get current quote for YStock
        ystock_price = nsequoter.get_futures_quote(YStock, current_date.strftime("%b"))
        #Get current quote for YStock
        xstock_price = nsequoter.get_futures_quote(XStock, current_date.strftime("%b"))
        current_data = pd.DataFrame([[0, 1], [ystock_price, xstock_price]], columns=columns)
        print colored('Current %s futures price: %s' % (YStock, ystock_price), 'cyan')
        print colored('Current %s futures price: %s' % (XStock, xstock_price), 'cyan')
        Y = np.asarray(data[YStock])
        X = np.asarray(data[XStock])
        _y = np.append(Y, current_data.YStock)
        _x = np.append(X, current_data.XStock)
        model = linreg(Y=_y, X=_x)
        print colored('Model\'s current std error: %s\n' % get_current_std_err(model), 'yellow')

    except Exception,e:
        print colored('Unable to fetch current futures price','red')
        print e
    #print colored('Successfully read file: %s' % constants.current_filename,'cyan')

    pass
