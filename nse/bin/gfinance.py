from googlefinance import getQuotes
import json

def getcurrent(stock):
    print json.dumps(getQuotes(symbols=stock), indent=2)

    return

def main():
    getcurrent('SBIN')
