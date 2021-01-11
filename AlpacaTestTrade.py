#!/usr/bin/env python
# coding: utf-8

# In[6]:


import alpaca_trade_api as tradeapi
import threading
from time import sleep 
import json
import logging

#authentication and connection details
APCA_API_KEY_ID = 'PKC7N32R5TA33ABKOWFI'
APCA_API_SECRET_KEY = 'XrQUKqXhcKBrUP1bGdFJos88acVn2N7PYEJDkLXu'
APCA_API_BASE_URL = 'https://paper-api.alpaca.markets'

#instantiate REST API
api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL, api_version='v2')

#obtain account information
account = api.get_account()
print(account)


# In[7]:


api.submit_order(symbol='SPCE', 
    qty=1, 
    side='buy', 
    time_in_force='gtc', 
    type='market')
    #limit_price=400.00, 
    #client_order_id='001'


# In[ ]:




