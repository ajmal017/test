import pandas as pd
import pandas.io.data
import numpy as np
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-darkgrid')

pd.set_option('display.notebook_repr_html', True)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 10)
pd.set_option('display.width', 100)
pd.set_option('precision', 3)

plotPath = "/Users/abhishek.chaturvedi/PycharmProjects/self/test/data/"


def fillAndSavePlot(title, x=False, y=False, suptitle=False, legendLOC=2):
    if suptitle == True:
        plt.suptitle(suptitle, fontsize=25, fontweight="bold")
    else:
        plt.title(title, fontsize=25, fontweight="bold")
        if type(x) == str:
            plt.xlabel(x, fontsize=18)
        if type(y) == str:
            plt.ylabel(y, fontsize=18)

    plt.annotate("AUTHOR: Karan Sagoo", xy=(0, 0), xycoords='axes fraction', alpha=0.1, fontsize=20)
    plt.legend(loc=legendLOC)
    plt.tight_layout()
    path = plotPath
    plt.savefig(plotPath + title + ".png", bbox_inches='tight', dpi=300)


def fillAndSavePlot1(name, title, x=False, y=False, suptitle=False, legendLOC=2):
    if suptitle == True:
        plt.suptitle(suptitle, fontsize=25, fontweight="bold")
    else:
        name.set_title(title, fontsize=25, fontweight="bold")
        if type(x) == str:
            name.set_xlabel(x, fontsize=18)
        if type(y) == str:
            name.set_ylabel(y, fontsize=18)

    name.annotate("AUTHOR: Karan Sagoo", xy=(0, 0), xycoords='axes fraction', alpha=0.1, fontsize=20)
    name.legend(loc=legendLOC)
    plt.tight_layout()
    path = plotPath
    plt.savefig(plotPath + title + ".png", bbox_inches='tight', dpi=300)

start = datetime.date(2017, 1, 1)
end = datetime.date(2017, 5, 1)


def get(tickers, start, end):
    def data(ticker):
        return pd.io.data.DataReader(ticker, 'yahoo',
                                     start, end)

    datas = map(data, tickers)

    return pd.concat(datas, keys=tickers,
                     names=['Ticker', 'Date'])

tickers = ['SBIN.NS','ITC.NS','ONGC.NS','PNB.NS','VAKRANGEE.NS','CAPF.NS']
all_data = get(tickers, start, end)
just_closing_prices = all_data[['Adj Close']].reset_index()
daily_close_px = just_closing_prices.pivot('Date','Ticker','Adj Close')

#Plotting Closing Price for all Stocks
#_ = daily_close_px.plot(figsize=(12,8));
#fillAndSavePlot(title = "Closing Price for All Companies",x="Date", y="Closing Price (INR)")
#Plotting Volume Series Data for Apple
#aaplV = all_data.Volume.loc['AAPL']
#plt.bar(aaplV.index, aaplV)
#plt.gcf().set_size_inches(12,6)
#fillAndSavePlot(title="Volume Series - Apple", x="Date", y= "Price (INR)")

#Daily Percent Change
# to make this easy, pandas has .pct_change() baked in
daily_pct_change = daily_close_px.pct_change()
daily_pct_change.fillna(0, inplace=True)
#stock = daily_pct_change['SBIN.NS']
#print stock.describe()
#sns.distplot(stock)
#plt.rcParams['figure.figsize']=(12,8)
#fillAndSavePlot(title="Daily Percent Returns ",x="Percent Return (%) ")
# ploting all the cumulative return distributions
_ = daily_pct_change.hist(bins=50, sharex=True, figsize=(12,8));
plt.savefig('Percent return for all Stocks', bbox_inches='tight', dpi=300)
plt.show()

std1 = []
for col in list(daily_pct_change.columns):
    temp = (col, daily_pct_change[col].std())
    std1.append(temp)
aq = pd.DataFrame.from_records(std1, columns=["stock", "Standard Deviation"], index = "stock")
z = aq["Standard Deviation"].sort_values().to_frame()
d1 = daily_pct_change[list(z.index)].copy()
g = sns.violinplot(d1,scale="count")
fillAndSavePlot1(g,"Stocks Violin Plot - Increasing Standard Deviation",x= "Stock Name", y = "Percent Change (%)")
ax = sns.pairplot(daily_pct_change,diag_kind = "kde")
plt.show()


# use a minimum of 75 days
min_periods = 75
# calculate the rolling standard deviation
vol = pd.rolling_std(daily_pct_change, min_periods) * \
                     np.sqrt(min_periods)
# plot it
_ = vol.plot(figsize=(10, 8))
plt.savefig('5104OS_05_22.png', bbox_inches='tight', dpi=300)