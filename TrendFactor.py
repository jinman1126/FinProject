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
#import pandas_datareader.data as web
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
    symbol_list   = df.sort_values('MarketCap').Symbol.tail(500).values
    #industry_list = df.sort_values('Industry' ).Industry.values
    
    return(symbol_list)
    
symbol_list = get_universe()

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
                return(df,start)
        
            except Exception: #not enough data for consideration
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
  
def get_MA(df,start):
    
    MA_Output         = []
    MR_Output         = []
    Master_datelist   = []
    output = []
    Lags              = [3,5,10,20,50,100,200]
    df['Returns']     = df['Adj Close'].pct_change(21)
    
    for Lag in Lags:
        print(Lag)
        
        closes        = df['Adj Close']
        MA            = closes.rolling(Lag).mean()
        df['MA']      = MA
        ################################
        
        #now we need to get the value for
        #the first of each month
        #and return the list
        
        ################################
    
        #x helps us adjust start date based on the starting MA
        x                   = 1 + math.ceil(Lag/21)
        first_date          = start + timedelta(days=x*30)
        today               = datetime.datetime.now()
        last_date           = today.strftime('%Y')+'-'+today.strftime('%m')+'-1'
        first_BD_months     = pd.date_range(first_date.strftime('%Y-%m-%d'),last_date,freq = 'BMS') 
        
        MA_list         = []
        Monthly_Returns = []
        datelist        = []
        for date in first_BD_months:
            try:
                
                MA     =    df.get_value(date,'MA')
                Norm   = MA/df.get_value(date,'Adj Close')
                Return =    df.get_value(date,'Returns')
                MA_list.append(Norm)
                Monthly_Returns.append(Return)
                datelist.append(date)
                
            except Exception: #handle if the date falls on the weekend/holidy
                try:
                    
                    date1  = date+timedelta(days=1)
                    MA     =    df.get_value(date1,'MA')
                    Norm   = MA/df.get_value(date1,'Adj Close')
                    Return =    df.get_value(date1,'Returns')
                    MA_list.append(Norm)
                    Monthly_Returns.append(Return)                
                    datelist.append(date1)
                    
                except Exception: #handle if the date falls on the weekend/holidy
                    try:
                        
                        date2  = date+timedelta(days=2)
                        MA     =    df.get_value(date2,'MA')
                        Norm   = MA/df.get_value(date2,'Adj Close')
                        Return =    df.get_value(date2,'Returns')
                        MA_list.append(Norm)
                        Monthly_Returns.append(Return)
                        datelist.append(date2)
                        
                    except Exception:#handle if the date falls on the weekend/holidy
                        try:

                            date3  =  date+timedelta(days=3)
                            MA     =    df.get_value(date3,'MA')
                            Norm   = MA/df.get_value(date3,'Adj Close')
                            Return =    df.get_value(date3,'Returns')                  
                            MA_list.append(Norm)
                            Monthly_Returns.append(Return)
                            datelist.append(date3)
                            
                        except Exception:#handle if the date falls on the weekend/holidy
                            
                            date4  =  date+timedelta(days=4)
                            MA     =    df.get_value(date4,'MA')
                            Norm   = MA/df.get_value(date4,'Adj Close')
                            Return =    df.get_value(date4,'Returns')                  
                            MA_list.append(Norm)
                            Monthly_Returns.append(Return)
                            datelist.append(date4)
                            
        output_df = pd.DataFrame({'Date'        :datelist,
                               'MA'             :MA_list,
                               'Monthly Returns':Monthly_Returns})
        #print(output_df.head())
        output.append(output_df)
    return(output)
    
################################################################

#Define a method to handle Cross Sectional Regression for each
#symbol

################################################################
def cross_sectional_regression(dfs):
    
    df_list = []
    #rj,t = B0,t + sum Bi,tAjt-1Li + E j=1,...,n
    for df in dfs:
        
        MA         = df['MA'].values
        MR         = df['Monthly Returns'].values  
        df['MA-1'] = df['MA'].shift(1)

        i=1
        intercepts = []
        betas      = []
        betasum12  = []
        for i in range(len(MA)):
        
            intercept = MR[i] - MA[i]*MA[i-1]
            beta      = MA[i]*MA[i-1]
        
            intercepts.append(intercept)
            betas.append(beta)
            i+=1
            
        i=11
        for i in range(len(MA)):
            betasum = sum(MA[i-12:i])/12
            betasum12.append(betasum)
            i+=1
            
        df['Intercepts']          = pd.Series(intercepts,index = df.index)
        df['Betas']               = pd.Series(betas     ,index = df.index)
        df['BetaSum12']           = pd.Series(betasum12 ,index = df.index)
        df['Expected Return t+1'] = df['MA-1']*df['BetaSum12']
        
        
        
        print(df.head())        
        print(df.tail())
        df_list.append(df)

    return(df_list)
    
    
    
    
################################################################
symbols = get_universe()
print(symbols)

data = get_data(symbols)
df = data[0]
start = data[1]

dfs = get_MA(df,start)
cross_sectional_regression(dfs)







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