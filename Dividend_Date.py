#!/usr/bin/env python
# coding: utf-8

# In[15]:


#https://medium.com/c%C3%B3digo-ecuador/how-to-python-web-scrape-the-nasdaq-stock-ex-dividend-calendar-648b6063c659
import pandas, requests, calendar, datetime
from dateutil import parser
class dividend_calendar:
    #class attributes 
    calendars = [] 
    url = 'https://api.nasdaq.com/api/calendar/dividends'
    hdrs =  {'Accept': 'application/json, text/plain, */*',
                 'DNT': "1",
                 'Origin': 'https://www.nasdaq.com/',
                 'Sec-Fetch-Mode': 'cors',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)'}
    def __init__(self, year, month):
          '''
        Parameters
        ----------
        year : year int
        month : month int

        Returns
        -------
        Sets instance attributes for year and month of object.

          '''
          #instance attributes
          self.year = int(year)
          self.month = int(month)

    def date_str(self, day):
          date_obj = datetime.date(self.year, self.month, day)
          date_str = date_obj.strftime(format='%Y-%m-%d')     
          return date_str
    def scraper(self, date_str):
         ''' 
          Scrapes JSON object from page using requests module.

           Parameters
           - - - - - 
           url : URL string
           hdrs : Header information
           date_str: string in yyyy-mm-dd format

           Returns
           - - - -
           dictionary : Returns a JSON dictionary at a given URL.

         '''
         params = {'date': date_str}
         page=requests.get(self.url,headers=self.hdrs,params=params)
         dictionary = page.json()
         return dictionary

    def dict_to_df(self, dicti):
         ''' 
         Converts the JSON dictionary into a pandas dataframe
         Appends the dataframe to calendars class attribute         

         Parameters
         ----------
         dicti : Output from the scraper method as input.

         Returns
         -------
         calendar : Dataframe of stocks with that exdividend date

         Appends the dataframe to calendars class attribute

         If the date is formatted correctly, it will append a 
         dataframe to the calendars list (class attribute).  
         Otherwise, it will return an empty dataframe.         
         '''

         rows = dicti.get('data').get('calendar').get('rows')
         calendar = pandas.DataFrame(rows)
         self.calendars.append(calendar)
         return calendar


    def calendar(self, day):
          '''
          Combines the scrape and dict_to_df methods

          Parameters
          ----------
          day : day of the month as string or number.

          Returns
          -------
          dictionary : Returns a JSON dictionary with keys 
          dictionary.keys() => data, message, status

          Next Levels: 
          dictionary['data'].keys() => calendar, timeframe
          dictionary['data']['calendar'].keys() => headers, rows
          dictionary['data']['calendar']['headers'] => column names
          dictionary['data']['calendar']['rows'] => dictionary list

          '''
          day = int(day)
          date_str = self.date_str(day)      
          dictionary = self.scraper(date_str)
          self.dict_to_df(dictionary)          
          return dictionary

