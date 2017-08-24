import nsequoter as q
import os, sys

index = 'NIFTY'
tick = 'PNB'
monI = 'AUG'
monII = 'SEP'
monIII = 'OCT'
months = [monI, monII, monIII]
basket_stocks = ['PNB','SBIN']
basket_index = ['NIFTY','BANKNIFTY']
thresholds = {'NIFTY':40,'BANKNIFTY':60,'SBIN':1.5,'PNB':2}

def get_stock(tick, month):
    return q.get_futures_stock(tick, month)
def get_index(idx, month):
    return q.get_futures_idx(idx, month)

price_list = []
os.system('cls')
for each_tick in basket_index:
    for m in months:
        price_list.append(get_index(each_tick,m))
    print 'INDEX:',each_tick
    diff_mid_current = price_list[1] - price_list[0]
    diff_far_mid = price_list[2] - price_list[1]
    print '\tSpread: Mid -> Current\t', diff_mid_current
    print '\tSpread: Far -> Mid\t\n',diff_far_mid
    if diff_mid_current > 0 and diff_mid_current > thresholds[each_tick]:
        print 'Difference between Mid and Current is above Threshold.'
        print 'Sell %s and buy %s\n' %(monII,monI)
    elif diff_mid_current < 0 and diff_mid_current > thresholds[each_tick]:
        print 'Difference between Mid and Current is above Threshold.'
        print 'Sell %s and buy %s\n' %(monIII,monII)
        print
    elif diff_far_mid > 0 and diff_far_mid > thresholds[each_tick]:
        print 'Difference between Far and Mid is above Threshold.'
        print 'Sell %s and buy %s\n' % (monIII, monII)
        print
    elif diff_far_mid < 0 and diff_far_mid > thresholds[each_tick]:
        print 'Difference between Far and Mid is above Threshold.'
        print 'Sell %s and buy %s\n' %(monIII
                                     ,monII)
        print
    price_list = []

for each_tick in basket_stocks:
    for m in months:
        price_list.append(get_stock(each_tick,m))
    print 'STOCK:',each_tick
    diff_mid_current = price_list[1] - price_list[0]
    diff_far_mid = price_list[2] - price_list[1]
    print '\tSpread: Mid -> Current\t', diff_mid_current
    print '\tSpread: Far -> Mid\t',diff_far_mid
    if diff_mid_current > 0 and diff_mid_current > thresholds[each_tick]:
        print 'Difference between Mid and Current is above Threshold.'
        print 'Sell %s and buy %s\n' %(monII,monI)
        print
    elif diff_mid_current < 0 and diff_mid_current > thresholds[each_tick]:
        print 'Difference between Mid and Current is above Threshold.'
        print 'Sell %s and buy %s\n' %(monII,monI)
        print
    elif diff_far_mid > 0 and diff_far_mid > thresholds[each_tick]:
        print 'Difference between Far and Mid is above Threshold.'
        print 'Sell %s and buy %s\n' % (monIII, monII)
        print
    elif diff_far_mid < 0 and diff_far_mid > thresholds[each_tick]:
        print 'Difference between Far and Mid is above Threshold.'
        print 'Sell %s and buy %s\n' %(monIII
                                     ,monII)
        print
    price_list = []