# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 16:32:40 2017

@author: 63669
"""
import time
import datetime
from pytz import timezone 
import numpy as np
import pandas as pd
from scipy import stats
from pandas.tseries.offsets import BDay
import pandas_datareader.data as web
import statsmodels.api as sm

 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.linear_model import ARDRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.neural_network import MLPRegressor
api_key = 'wWCC6zREYitTDxLTi61d'

################################################################

#get symbol lists from nasdaq, nyse, amex. 
#Also pulls in makret cap data and other information.
#check out the URL for more information

################################################################

def get_universe():
    
    symbols_by_industry = {}
    
    nasdaq = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NASDAQ&render=download")
    nyse   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NYSE&render=download")
    amex   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=AMEX&render=download")
    df     = pd.concat([nasdaq, nyse, amex])
    
    print(len(df))
    symbol_list   = df.sort_values('MarketCap').Symbol.tail(1).values
    industry_list = df.sort_values('Industry' ).Industry.values
    
    for industry in set(industry_list):

        symbols_by_industry[industry] = df[df['Industry'] == industry].Symbol.tolist()
        
    return(symbols_by_industry)
    

################################################################

#define a method to retrieve historical data

################################################################

def get_data(symbol,end):
    
   #One_year   = end_date - Bday(252)
   #Two_year   = end_date - Bday(504)
    Three_year = end - BDay(756)    
    start      = Three_year.strftime('%Y-%m-%d')
    end        = end.strftime('%Y-%m-%d')
    f          = web.DataReader(symbol.strip(), 'yahoo', start, end).dropna(axis=0)
    start      = f.index[0]
    
    return(f, start)
    
################################################################


################################################################
  
date = datetime.datetime.now()
print(date.strftime('%Y'))
  
    
get_universe()
