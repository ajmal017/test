import requests
from contextlib import closing
import csv

url = "https://www.nseindia.com/archives/nsccl/volt/CMVOLT_18112016.CSV"

with closing(requests.get(url, stream=True)) as r:
    reader = csv.reader(r.iter_lines(), delimiter=',', quotechar='"')
    mydict = dict((rows[6], rows[1]) for rows in reader)

for key in sorted(mydict.iterkeys()):
    print "%s: %s" % (key, mydict[key])


#print(mydict['VEDL'])

