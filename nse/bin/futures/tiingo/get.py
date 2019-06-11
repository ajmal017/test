import requests

headers = {
        'Content-Type': 'application/json',
        'Authorization' : 'Token 021498e2ab08bcf6bdd864fff0792f403de8e64c'
        }
requestResponse = requests.get("https://api.tiingo.com/api/test/",
                                    headers=headers)
print(requestResponse.json())

requestResponse = requests.get("https://api.tiingo.com/tiingo/daily/aapl/prices?startDate=2019-05-01", headers=headers)
print(requestResponse.json())

requestResponse = requests.get("https://api.tiingo.com/tiingo/daily/googl/prices?startDate=2019-05-01&endDate=2019-05-06&format=csv", headers=headers)
print(requestResponse)

#https://api.tiingo.com/tiingo/daily/<ticker>/prices?startDate=2012-1-1&endDate=2016-1-1&format=csv&resampleFreq=monthly
