from datetime import datetime
import numpy as np
import alpaca_trade_api as tradeapi
import pandas as pd
import threading
from time import sleep 
import time as time
import json
import logging
import datetime
from dateutil import parser
import requests, calendar
from Dividend_Date import dividend_calendar
import math

APCA_API_KEY_ID = 'PKC7N32R5TA33ABKOWFI'
APCA_API_SECRET_KEY = 'XrQUKqXhcKBrUP1bGdFJos88acVn2N7PYEJDkLXu'
APCA_API_BASE_URL = 'https://paper-api.alpaca.markets'

######################
api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL, api_version='v2')
account = api.get_account()
print(account)
api.submit_order(symbol='SPCE', 
    qty=1, 
    side='buy', 
    time_in_force='gtc', 
    type='market')
    #limit_price=400.00, 
    #client_order_id='001'
##########

year = datetime.datetime.utcnow().year
month = datetime.datetime.utcnow().month
dividend_calendar(year,month) ###run the dividend_calendar class I imported
#get number of days in month
days_in_month = calendar.monthrange(year, month)[1]
#create calendar object    
ourmonth = dividend_calendar(year, month)
#define lambda function to iterate over list of days     
function = lambda days: ourmonth.calendar(days)
#define list of ints between 1 and the number of days in the month
iterator = list(range(1, days_in_month+1))
#Scrape calendar for each day of the month                    
objects = list(map(function, iterator))
#concatenate all the calendars in the class attribute
concat_df = pd.concat(ourmonth.calendars)
#Drop any rows with missing data
drop_df = concat_df.dropna(how='any')
#set the dataframe's row index to the company name
final_df = drop_df.set_index('companyName')

######################
account = api.get_account()
print(account)
api.submit_order(symbol='AAPL', 
    qty=1, 
    side='buy', 
    time_in_force='gtc', 
    type='market')
    #limit_price=400.00, 
    #client_order_id='001'
##########


class SMAStrat:
    def __init__(self):
        self.alpaca = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL, api_version='v2')
        self.barTimeframe = "day" # 1Min, 5Min, 15Min, 1H, 1D
        self.assetsToTrade = ["TQQQ", "QID"]
        #self.assetsToTrade = ["NUGT","TQQQ", "QID", "CCL", "SPXS", "SPXL"]
        self.positionSizing = (1/self.possizing())
        self.timeList = []
        self.openList = []
        self.highList = []
        self.lowList = []
        self.closeList = []
        self.volumeList = []
    
    def run(self):
        # First, cancel any existing orders so they don't impact our buying power.
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
          self.alpaca.cancel_order(order.id)

        # Wait for market to open.
        print("Waiting for market to open...")
        tAMO = threading.Thread(target=self.awaitMarketOpen)
        tAMO.start()
        tAMO.join()
        print("Market opened.")
        while True:

          # Figure out when the market will close so we can prepare to sell beforehand.
          clock = self.alpaca.get_clock()
          closingTime = clock.next_close.replace(tzinfo=datetime.timezone.utc).timestamp()
          currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
          self.timeToClose = closingTime - currTime

          if(self.timeToClose < (60 * 5)):
            # Stop Trading when 5 minutes til market close.
            print("Market closing soon. No Longer Trading.")
            # Run script again after market close for next trading day.
            print("Sleeping until market close (5 minutes).")
            time.sleep(60 * 15)
          else:
            # Rebalance the portfolio.
            for symbol in self.assetsToTrade:
                self.dataset = self.alpaca.get_barset(symbol,self.barTimeframe,limit=100).df
                tSMA = threading.Thread(target=self.calculateSMAs(symbol))
                tSMA.start()
                tSMA.join()
                tRebalance = threading.Thread(target=self.buyselldecision(symbol))
                tRebalance.start()
                tRebalance.join()
            time.sleep(60*10) ###This determines how frequently it runs. a value of 60 would mean every minute
        
  # Wait for market to open.
    def awaitMarketOpen(self):
        isOpen = self.alpaca.get_clock().is_open
        while(not isOpen):
          clock = self.alpaca.get_clock()
          openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
          currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
          timeToOpen = int((openingTime - currTime) / 60)
          print(str(timeToOpen) + " minutes til market open.")
          time.sleep(60)
          isOpen = self.alpaca.get_clock().is_open
    
    def MA(self,df, n):  #######Carson Created from https://www.quantopian.com/posts/technical-analysis-indicators-without-talib-code
        MA = pd.Series((df['close'].rolling(window=n).mean()), name = 'MA_' + str(n))  
        df = df.join(MA)  
        return df

# Tracks position in list of symbols to download
    def calculateSMAs(self, symbol):
        self.SMA20=0
        self.SMA50=0
        SMA20df = self.MA(self.dataset[symbol],20)
        self.SMA20=SMA20df['MA_20'].values[-1]
        SMA50df = self.MA(self.dataset[symbol],50)
        self.SMA50=SMA50df['MA_50'].values[-1]
                               
    def possizing(self):
        self.SMA2099=0
        self.count=0
        for symbol in self.assetsToTrade:
            self.dataset = self.alpaca.get_barset(symbol,self.barTimeframe,limit=100).df
            self.p = self.alpaca.get_last_trade(symbol).price
            self.SMA20df99 = self.MA(self.dataset[symbol],20)
            self.SMA2099=(self.SMA20df99['MA_20'].values[-1])*.99
            if self.p > self.SMA2099:
                self.count+=1
        return self.count
        
# Determines if stock has div ex date coming up
    def dividenddates(self,symbol):
        try:
            self.divdate = final_df.loc[final_df['symbol'] == symbol].dividend_Ex_Date.values
            self.daystilldiv = ((parser.parse(divdate[0]) - datetime.utcnow())).days
        except:
            self.daystilldiv =100 ######arbitrarily using 100 b/c it's far out
    # Calculates the trading signals
    def buyselldecision(self, symbol):
        price = self.alpaca.get_last_trade(symbol).price
        self.dividenddates(symbol)
        print("tried" + symbol + "| P"+str(price)+ "| SMA"+str(self.SMA20))
        #print('price '+str(price))
        #print('SMA20 '+str(self.SMA20))
        try:
            openPosition = int(self.alpaca.get_position(symbol).qty)
        except:
            # No position exists
            openPosition = 0
        print('current holding:'+ str(openPosition))
        if price > self.SMA20:
            # Opens new position if one does not exist
            if openPosition <= 0:
                self.positionSizing = (1/self.possizing())
                cashBalance = self.alpaca.get_account().cash
                targetPositionSize = math.floor((float(cashBalance) * self.positionSizing) // price) # Calculates required position size

                returned = self.alpaca.submit_order(symbol,targetPositionSize,"buy","market","gtc") # Market order to open position
                print(returned)

        else:
            # Closes position if SMA20 is below SMA50
            if openPosition > 0 and self.daystilldiv>5:
                try:
                    #SellMinusOne = openPosition -1
                    returned = self.alpaca.submit_order(symbol,openPosition,"sell","market","gtc") # Market order to fully close position
                    print(returned)
                except: 
                    print('maintaining 1 share')
    
    
SMAS = SMAStrat()
SMAS.run()
