# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 16:32:40 2017

@author: 63669
"""
import time
import datetime
from datetime import timedelta
from pytz import timezone 
import numpy as np
import pandas as pd
from scipy import stats
from pandas.tseries.offsets import BDay
import pandas_datareader.data as web
import statsmodels.api as sm
import math

 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.linear_model import ARDRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.neural_network import MLPRegressor
api_key = 'wWCC6zREYitTDxLTi61d'
errorlist = {}

################################################################

#get symbol lists from nasdaq, nyse, amex. 
#Also pulls in makret cap data and other information.
#check out the URL for more information

################################################################

def get_universe():
    
    #symbols_by_industry = {}
    
    nasdaq = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NASDAQ&render=download")
    nyse   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NYSE&render=download")
    amex   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=AMEX&render=download")
    df     = pd.concat([nasdaq, nyse, amex])
    
    print(len(df))
    symbol_list   = df.sort_values('MarketCap').Symbol.tail(1).values
    #industry_list = df.sort_values('Industry' ).Industry.values
    
    return(symbol_list)
    

################################################################

#define a method to retrieve historical data
#Included a retry count in case there are connection issues

################################################################

def get_data(symbol):
    
    retry_count = 0
    try:
        while retry_count < 5:
            try:        
                #last business day
                Today    = (datetime.datetime.now() + BDay(0))
                Start    = (Today - BDay(15*252))
        
                Today=Today.strftime('%Y-%m-%d')
                Start=Start.strftime('%Y-%m-%d')
        
                df         = web.DataReader(symbol[0], 'yahoo', Start, Today).dropna(axis=0)
                start      = df.index[0]
                retry_count+=5
                df.drop('Open',axis=1)
                df.drop('High',axis=1)
                df.drop('Low',axis=1)
                df.drop('Close',axis=1)
                return(df,start)
        
            except Exception: #not enough data for consideration
                print(retry_count)
                retry_count+=1
    
    except Exception:
        errorlist[symbol] = 'error retrieving data'        
        return None
    
################################################################

#Define a method to get Moving Average for each month 
# at various lags. we will have 3,5,10,20,100,200 day MA's
#Also get the monthly returns estimated assuming 21 business days
#per month.

################################################################
  
def get_MA(df,start,Lag):
        
    closes            = df['Adj Close']
    MA_Short          = closes.rolling(Lag[0]).mean()
    MA_Long           = closes.rolling(Lag[1]).mean()
    df['Short']       = MA_Short
    df['Long']        = MA_Long
        
    dates             = df.index
    Trend_List        = []
    i=0
        
    try:
        for i in range(len(dates)-2):
            #print(i+Lag[1])
            if df.get_value(dates[i+Lag[1]],'Short') > df.get_value(dates[i+Lag[1]],'Long'):
                Trend_Direction = 1
                Trend_List.append(Trend_Direction)
                i+=1
                    
            else:
                Trend_Direction = 0
                Trend_List.append(Trend_Direction)
                i+=1 
                
    except Exception: 
        
        x=1        
        for x in range(Lag[1]):
            Trend_List.insert(0,0)
            x+=1
            
        i=1
        reversals = []
        for i in range(len(Trend_List)):
            
            x = Trend_List[i-1] - Trend_List[i]
            if x == 1:
                reversal = -1
                reversals.append(reversal)
                
            elif x == 0:
                reversal = 0
                reversals.append(reversal)
                
            elif x == -1:
                reversal = 1
                reversals.append(reversal)
                
            else:
                reversal = 0
                reversals.append(reversal)
                
        df['Trend Direction'] = pd.Series(Trend_List,index = df.index)
        df['Reversals']       = pd.Series(reversals ,index = df.index)   
        
        return(df)
    
################################################################

#Define a method to calculate average returns and average accuracy

################################################################
    
    
    
    
    
    
################################################################
symbols = get_universe()
print(symbols)

data = get_data(symbols)
df   = data[0]
#df['Monthly Returns']     = df['Adj Close'].pct_change(21)

start = data[1]
Lags = [[5,100],[5,150],[5,200],[5,250],[10,50],[10,100],[10,150],[10,200],[10,250],[20,50],[20,100],[20,150],[20,200],[20,250],[50,100],[50,150],[50,200],[50,250]]
df_list = []
for lag in Lags:

    df = get_MA(df,start,lag)
    df_list.append(df)
    #print(df.tail(100))
print(df_list[8].tail(100))

    








'''
    year                = start.strftime('%Y')
    month               = start.strftime('%m')+1
    day                 = start.strftime('%d')
    
    if month == 13:
        month = 1
    
    first_date          = year+'-'+month+'-1'
    today               = datetime.datetime.now()
    last_date           = today.strftime('%Y')+'-'+today.strftime('%m')+'-1'
    
    first_BD_months     = pd.date_range(first_date,last_date,freq = 'BMS') 
'''