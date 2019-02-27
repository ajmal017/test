#! /usr/bin/python3

import pprint
import time
import datetime
import logging
import argparse
import sys
import numpy
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
from imgurpython import ImgurClient
import praw

from tdameritrade import TDClient
import tdameritrade.auth

client_id = 'IMGUR_ID'
client_secret = 'IMGUR_SECRET'

closed = ["01-01-2019", "01-21-2019", "02-18-2019", "04-19-2019",
          "05-27-2019", "07-04-2019", "09-02-2019", "11-28-2019",
          "12-25-2019"]

tickers = ["NDX", "RUT", "AAPL", "AMD", "AMZN",
           "BA", "DIS", "FB", "MSFT", "NFLX",
           "QQQ", "SQ", "TSLA", "V"]


def getColor(letter):
    # Colorgorical http://vrl.cs.brown.edu/color
    if letter == "A":
        return (79, 140, 157)
    elif letter == "B":
        return (139, 208, 235)
    elif letter == "C":
        return (102, 127, 66)
    elif letter == "D":
        return (164, 247, 137)
    elif letter == "E":
        return (212, 95, 234)
    elif letter == "F":
        return (46, 206, 183)
    elif letter == "G":
        return (223, 42, 105)
    elif letter == "H":
        return (243, 247, 152)
    elif letter == "I":
        return (45, 109, 249)
    elif letter == "J":
        return (247, 197, 241)
    elif letter == "K":
        return (32, 182, 71)
    elif letter == "L":
        return (236, 75, 24)
    elif letter == "M":
        return (247, 147, 2)
    else:
        return (255, 255, 255)


def findPrecision(top):
    # decide how many decimals of precision we use
    # based on price
    if top < 3:
        return 2
    elif top < 500:
        return 1
    else:
        return 0


def getLetter(hour, minute):
    # match 30 minute increments to letters
    if hour == 7 and minute >= 30:
        return "A"
    elif hour == 8 and minute < 30:
        return "B"
    elif hour == 8 and minute >= 30:
        return "C"
    elif hour == 9 and minute < 30:
        return "D"
    elif hour == 9 and minute >= 30:
        return "E"
    elif hour == 10 and minute < 30:
        return "F"
    elif hour == 10 and minute >= 30:
        return "G"
    elif hour == 11 and minute < 30:
        return "H"
    elif hour == 11 and minute >= 30:
        return "I"
    elif hour == 12 and minute < 30:
        return "J"
    elif hour == 12 and minute >= 30:
        return "K"
    elif hour == 13 and minute < 30:
        return "L"
    elif hour == 13 and minute >= 30:
        return "M"


def fp(number, precision):
    # returns a string from a float with a variable precision
    return '{:.{}f}'.format(number, precision)


def tpoSymbol(data):
    # main worker thread, takes TDA data as input, returns imgur link of final product

    # setup some vars to sort things into
    top = 0
    bottom = 1000000
    days = []
    highest = 0
    # first pass through TDA to find highest value, determines how many decimal points to care about later.
    for line in data['candles']:
        if line['high'] > highest:
            highest = line['high']
    precision = findPrecision(highest)
    logging.info("Highest was %s, precision set to %s" % (highest, precision))
    # second pass through TDA data to determine dates and the lows and highs covered in the set
    for line in data['candles']:
        day = datetime.datetime.fromtimestamp(line['datetime'] / 1000).strftime("%m-%d-%Y")
        if day not in days:
            days.append(day)
        high = line['high'] * 10 ** precision
        low = line['low'] * 10 ** precision
        if high > top:
            top = high
        if low < bottom and low > 0:
            bottom = low
    bottom = bottom / 10 ** precision
    top = top / 10 ** precision
    logging.info("Range = %s - %s" % (bottom, top))
    prices = []

    for p in numpy.arange(bottom, top + (1 / 10 ** precision), 1 / 10 ** precision):
        prices.append(fp(p, precision))
    prices = sorted(prices, reverse=True)
    # full ends up being a dict of dicts with day being the outer key and price being the inner key
    full = defaultdict(str)

    # init full with blanks to cover instances where we didn't have price action
    for day in days:
        full[day] = {}
        for i in numpy.arange(bottom, top + 1 / 10 ** precision, 1 / 10 ** precision):
            full[day][fp(i, precision)] = ''
    # third pass through TDA data, this time to populate price/hour action into full
    for line in data['candles']:
        thistime = datetime.datetime.fromtimestamp(line['datetime'] / 1000)
        thisdate = thistime.strftime("%m-%d-%Y")
        high = round(line['high'], precision)
        low = round(line['low'], precision)
        for i in numpy.arange(low, high + 1 / 10 ** precision, 1 / 10 ** precision):
            letter = getLetter(thistime.hour, thistime.minute)
            try:
                if letter not in full[thisdate][fp(i, precision)]:
                    full[thisdate][fp(i, precision)] += letter
            except:
                pass
    # output is a list of lines used to generate the final image
    output = []
    # spacer is used the first column based on largest vlaue
    spacer = len(fp(top, precision)) + 2
    output.append(
        "+" + "-" * spacer + "+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+")
    output.append("|" + " " * spacer + "| " + '{:^13}'.format(days[0]) + " | "
                  + '{:^13}'.format(days[1]) + " | "
                  + '{:^13}'.format(days[2]) + " | "
                  + '{:^13}'.format(days[3]) + " | "
                  + '{:^13}'.format(days[4]) + " | "
                  + '{:^13}'.format(days[5]) + " | "
                  + '{:^13}'.format(days[6]) + " | "
                  + '{:^13}'.format(days[7]) + " | "
                  + '{:^13}'.format(days[8]) + " | "
                  + '{:^13}'.format(days[9]) + " | ")
    output.append(
        "+" + "-" * spacer + "+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+")
    for line in prices:
        # format based on spacer to ensure we remain the same width even if total digits
        # in price changes midstream (ie 99 to 100)
        n = ("{0:>" + str(spacer) + "}").format(line + ' ')
        output.append("|" + n + '| {0: <13}'.format(full[days[0]][line]) + " | " +
                      '{0: <13}'.format(full[days[1]][line]) + " | " +
                      '{0: <13}'.format(full[days[2]][line]) + " | " +
                      '{0: <13}'.format(full[days[3]][line]) + " | " +
                      '{0: <13}'.format(full[days[4]][line]) + " | " +
                      '{0: <13}'.format(full[days[5]][line]) + " | " +
                      '{0: <13}'.format(full[days[6]][line]) + " | " +
                      '{0: <13}'.format(full[days[7]][line]) + " | " +
                      '{0: <13}'.format(full[days[8]][line]) + " | " +
                      '{0: <13}'.format(full[days[9]][line]) + " | "
                      )
    output.append(
        "+" + "-" * spacer + "+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+")
    output.append("|" + " " * spacer + "| " + '{:^13}'.format(days[0]) + " | "
                  + '{:^13}'.format(days[1]) + " | "
                  + '{:^13}'.format(days[2]) + " | "
                  + '{:^13}'.format(days[3]) + " | "
                  + '{:^13}'.format(days[4]) + " | "
                  + '{:^13}'.format(days[5]) + " | "
                  + '{:^13}'.format(days[6]) + " | "
                  + '{:^13}'.format(days[7]) + " | "
                  + '{:^13}'.format(days[8]) + " | "
                  + '{:^13}'.format(days[9]) + " | ")
    output.append(
        "+" + "-" * spacer + "+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+---------------+")

    # use PIL to generate the final image

    # all white version

    # fnt = ImageFont.truetype('/home/tkammere/kivy/kivy/data/fonts/RobotoMono-Regular.ttf', 15)
    # img = Image.new('RGB', (1550, len(output)*17), color = (0, 0, 0))
    # d = ImageDraw.Draw(img)
    # for count,line in enumerate(output):
    #     d.text((10,count*17), line, font=fnt, fill=(255,255,255))
    # img.save(days[9]+".png")

    # color version
    fnt = ImageFont.truetype('RobotoMono-Regular.ttf', 15)
    xSize = 10
    ySize = 15
    img = Image.new('RGB', (len(output[0] * xSize), len(output) * ySize), color=(0, 0, 0))
    d = ImageDraw.Draw(img)
    for y, line in enumerate(output):
        for x, letter in enumerate(line):
            d.text((x * xSize, y * ySize), letter, font=fnt, fill=getColor(letter))
    img.save(days[9] + ".png")

    # huck it to imgur
    client = ImgurClient(client_id, client_secret)
    cred = client.credits
    logging.info("Imgur Credits:\n\t\t\t\tClientRemaining = %s\n\t\t\t\tUserRemaining = %s" % (
    cred['ClientRemaining'], cred['UserRemaining']))
    image = client.upload_from_path(days[9] + ".png", anon=True)
    logging.info("Posted to %s" % image['link'])
    return image['link']


def main(args):
    # setup TDA API
    authReply = tdameritrade.auth.authentication("abhishekda1423", "http://localhost")
    ACCESS_TOKEN = authReply['access_token']
    REFRESH_TOKEN = authReply['refresh_token']
    logging.info("Access token = %s" % ACCESS_TOKEN)
    c = TDClient(ACCESS_TOKEN)
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    isHoliday = today in closed
    logging.info("Today is %s, isHoliday = %s" % (today, isHoliday))
    if isHoliday:
        logging.error("Holiday exit")
        sys.exit(0)

    # get SPX History.  This appears to only be available the day after (12:01 CST)
    SPXImage = tpoSymbol(c.tpoHistory('SPX'))

    tickerImages = defaultdict()
    for ticker in tickers:
        tickerImages[ticker] = tpoSymbol(c.tpoHistory(ticker))

    # post it to reddit
    r = praw.Reddit("TPO")
    d = datetime.datetime.today()
    dFormat = d.strftime("%m-%d-%Y")
    title = "Daily SPX TPO's %s" % dFormat
    url = SPXImage
    subreddit = r.subreddit('thewallstreet').submit(title, url=url, send_replies=True)
    replyTemplate = 'New to Market profile? ' \
                    '[Check out this guide](http://www.ranchodinero.com/volume-tpo-essentials/) ' \
                    'and [this book](https://web.archive.org/web/20170829185705/https://www.cmegroup.com/education/interactive/marketprofile/handbook.pdf)\n\n \n\n' \
                    'Additional tickers (PM or reply in these threads if you want one added)\n\n'
    for ticker in tickers:
        replyTemplate += '[%s](%s)\n\n' % (ticker, tickerImages[ticker])

    subreddit.reply(replyTemplate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='SPX TPO generator')
    parser.add_argument(
        '--debug', '-v',
        action='store_true',
        help='More liiiiiiiiiiiines')
    parser.add_argument(
        '--nomarketcheck', '-m',
        action='store_true',
        help='Disable check if market is open')

    args = parser.parse_args()
    if args.debug:
        level = logging.DEBUG
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
    else:
        level = logging.ERROR

    logging.basicConfig(stream=sys.stdout, level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)

    main(args)