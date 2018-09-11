import numpy as np
from statsmodels import regression
import statsmodels.api as sm
import matplotlib.pyplot as plt
import math

def linreg(X,Y):
	# Running the linear regression
	X = sm.add_constant(X)
	model  = regression.linear_model.OLS(Y,X).fit()
	a = model.params[0]
	b = model.params[1]
	X = X[:, 1]
	
	# Return the summary of the regression and plot results
	X2 = np.linspace(X.min(), X.max(), 100)
	Y_hat = X2 * b + a
	plt.scatter(X,Y,alpha=0.3)
	plt.plot(X2, Y_hat, 'r', alpha=0.9);
	plt.xlabel('X Value')
	plt.ylabel('Y Value')
	return model.summary()

def linreg_(x,y):
	x = sm.add_constant(x)
	model = regression.linear_model.OLS(y,x).fit()
	# Remove the constant now that we're done
	x = x[:,1]
	return model.params
	