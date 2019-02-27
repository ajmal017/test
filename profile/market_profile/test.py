####
# Convert Pi Zerodha excel/csv file download to Amibroker format
####
import pandas as pd

directory = 'C://Zerodha//Pi/Exported//'
name = 'Nifty 50.csv'

header = ['Timestamp','Open','High','Low','Close','Volume']
df = pd.read_csv(directory+name, skiprows=1, names=header, parse_dates=['Timestamp'])
new_dates, new_times = zip(*[(d.date(), d.time()) for d in df['Timestamp']])
df = df.assign(Date = new_dates, Time = new_times)
df.set_index('Date')
columns = ['Open','High','Low','Close','Volume','Date','Time']
df1 = df.drop('Timestamp', axis=1)
print df1.head()
csv = directory + 'updated.csv'
df1.to_csv(csv,columns=columns, index=False)
