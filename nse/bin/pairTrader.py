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

##Reference:
## https://stackoverflow.com/questions/32101233/appending-predicted-values-and-residuals-to-pandas-dataframe
## Quantopian Lecture: https://www.quantopian.com/posts/quantopian-lecture-series-linear-regression
timestr = time.strftime("%Y%m%d")

location = "/Users/abhishek.chaturvedi/Downloads/Rough/projects/test/data/"


def zscore(series):
    return (series - series.mean()) / np.std(series)


def create_file_from_df(fName, df):
    try:
        df.to_csv(location + '%s' % fName)

    except Exception, e:
        print e

    print 'Created file : %s' % fName
    return None

def usfutures(basket, filename):

    timestr = time.strftime("%m-%d-%Y")
    columns = ['Time','Open','High','Low','Close','Change','Volume','Open Interest']
    for k,v in enumerate(basket):
        name = location + v + '_price-history-%s.csv' % timestr
        if not os.path.isfile(name):
            print 'File %s not present. Please download.' % name
            exit(0)

    name = location + basket[0] + '_price-history-%s.csv' % timestr
    first_stock = pd.read_csv(name, names=columns, skiprows=1)
    for i in range(1,len(basket)):
        _ = location + basket[i] + '_price-history-%s.csv' % timestr
        dfstock = pd.read_csv(_, names=columns, skiprows=1)
        if i == 1:
            data = pd.concat([first_stock['Close'].rename(basket[0]),
                              dfstock['Close'].rename(basket[i])],
                             axis=1)
        else:
            data = pd.concat([data, dfstock['Close'].rename(basket[i])],
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
    first_stock = nsepy.get_history(symbol=basket[0], start=sTime, end=eTime)

    for i in range(1, len(basket)):
        dfstock = nsepy.get_history(symbol=basket[i], start=sTime, end=eTime)

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
    return model.bse[0]
def get_std_err(model):
    return model.resid.std()
def get_std_err_ratio(model):
    ##Choose the least std error ratio
    return get_std_err_intercept(model) / get_std_err(model)
def get_alpha(model):
    return model.params[0]
def get_beta(model):
    return model.params[1]
def get_pvalue(model):
    return model.f_pvalue
def get_current_std_err(model):
    return model.resid[-1] / get_std_err(model)

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
                pairs.append((keys[i], keys[j]))
    return score_matrix, pvalue_matrix, pairs

def set_values(model, Y, X):
    ## Create an empty dataframe and then insert the model values to it
    ## Returns True on successfull work

    rows_list = []
    rows_list.append(Y)
    rows_list.append(X)
    rows_list.append(get_pvalue(model))
    rows_list.append(get_beta(model))
    rows_list.append(get_std_err_ratio(model))
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

def find_linear_regression_pairs(data, filename):
    """
    input: dataframe containing a basket of stock closing prices
    :return Nothing, just create the file
    ## Perform linear regression on all the possible pairs in the provided basket of stocks
    ## Store their OLS model results and write them out to a csv file
    """
    header = ['YStock', 'XStock', 'PValue', 'Beta', 'STD_ERR_Ratio', 'Alpha', 'Current_STD_Error']
    running_df = pd.DataFrame(columns=header)
    qualified_df = pd.DataFrame(columns=header)
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

    name = location+'pairtrade_'+filename
    running_df.to_csv(name)
    print 'Created pair trader file: %s' % (name)
    return None

def find_linear_regression_pairs_qualified(data, pairs, filename):
    """
    Perform linear regression on only the selected pairs after COINT
    Store the OLS model results in a csv file
    Selection Criteria:
        1. Compare the STD_ERRROR Ratio of Intercept / Std. Err of residuals and select the YStock which has this ratio minimum
        2. Filter for only those Y:X stock pairs which have the std_err (variance of current residuals) above or below the 1SD/2SD
    """

    header = ['YStock', 'XStock', 'PValue', 'Beta', 'STD_ERR_Ratio', 'Alpha', 'Current_STD_Error']
    qualified_df = pd.DataFrame(columns=header)

    keys = data.keys()
    for k,v in pairs:
        Y = np.asarray(data[k])
        X = np.asarray(data[v])
        model = linreg(Y=Y, X=X)
        inverse_model = linreg(Y=X, X=Y)

        if get_std_err_ratio(model) < get_std_err_ratio(inverse_model):
            #print '\tChoosing YStock : %s XStock: %s' % (keys[i],keys[j])
            if abs(get_current_std_err(model)) > 2.0:
                qualified_df.loc[len(qualified_df)] = set_values(model, Y=k, X=v)
        else:
            #print '\tChoosing YStock : %s XStock: %s' % (keys[j], keys[i])
            if abs(get_current_std_err(model)) > 2.0:
                qualified_df.loc[len(qualified_df)] = set_values(inverse_model, Y=v, X=k)

    name = location+'qualified_'+filename
    if not qualified_df.empty:
        qualified_df.to_csv(name)
        print 'Created qualified pair trader file: %s' % (name)
    else:
        print 'No qualified pairs identified.'
    return None
