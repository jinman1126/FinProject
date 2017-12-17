# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 21:12:53 2017

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

global_start_time = time.time()

################################################################
    
#Define a method to get Fama French Data. It also will return
#the last date of the FF data so we can parse the finace data
    
################################################################
    
def get_ff_data():
    
    url               = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
   #url2              = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip"
    
    ff                = pd.read_csv(url, compression='zip', header=2, index_col = [0], sep=',',parse_dates=[0])
    end_date          = ff.index[-1]
    
    return(ff,end_date)

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
    
#Define a method to format and combine the fama french dataframe
# and the daily price dataframe. 
#Also add a column for net returns calculated as a daily %change - RF
    
################################################################
    
def combine_data(df,ff,start,end):
    
    ff = pd.DataFrame(ff.loc[start:])
    df = pd.DataFrame(df.loc[:end])
        
    df['RF']          = ff['RF'].values
    df['Mkt-RF']      = ff['Mkt-RF'].values
    df['SMB']         = ff['SMB'].values
    df['HML']         = ff['HML'].values
    df['RMW']         = ff['RMW'].values
    df['CMA']         = ff['CMA'].values
    df['Net Returns'] = df['Adj Close'].pct_change(1) - df['RF']
        
    return(df)
    
###############################################################

#Define a method to perform Multiple Regression Analysis for
#CAPM, FF3, Carhart 4-Factor, and FF5 models. 
#           y = net returns
#           x = Mkt-RF
#FF3:       x = Mkt-RF + SMB + HML
#5-Factor   x = Mkt-RF + SMB + HML + RMW + CMA
###############################################################

def Regression(df):
    
    Y=df['Net Returns']
    
    CAPM_X     =                 df['Mkt-RF']
    FF3_X      = sm.add_constant(df[['Mkt-RF','SMB','HML']])
    FF5_X      = sm.add_constant(df[['Mkt-RF','SMB','HML','RMW','CMA']])
        
    CAPM_Model   = sm.OLS(Y,CAPM_X).fit()
    CAPM_Summary = CAPM_Model.summary()
    
    FF3_Model    = sm.OLS(Y,FF3_X).fit()
    FF3_Summary  = FF3_Model.summary()
    
    FF5_Model    = sm.OLS(Y,FF5_X).fit()
    FF5_Summary  = FF5_Model.summary()
    
    print('CAPM')
    print()
    print(CAPM_Summary)
    print()
    print('FF3')
    print()
    print(FF3_Summary)
    print()
    print('FF5')
    print()
    print(FF5_Summary)
    
    return(CAPM_Summary,FF3_Summary,FF5_Summary)

###############################################################
    
#Run program using the defined methods

###############################################################

ff_data   = get_ff_data()
ff        = ff_data[0]
end       = ff_data[1]

data      = get_data('aapl',end)
start     = data[1]
df        = data[0]

final     = combine_data(df,ff,start,end)[1:]
final.drop(final.index[0])

regression = Regression(final)    
'''
################################################################

#get symbol lists from nasdaq, nyse, amex. 
#Also pulls in makret cap data and other information.
#check out the URL for more information

################################################################

nasdaq = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NASDAQ&render=download")
nyse   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NYSE&render=download")
amex   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=AMEX&render=download")
symbols_combined   = pd.concat([nasdaq, nyse, amex])
symbol_list = symbols_combined.sort_values('MarketCap').Symbol.tail(1).values

print(symbol_list)

################################################################

#Get Fama French Factors

################################################################





#################################################################

#Get the first and last row numbers for each 
#Dataframe so we can match them up

#################################################################

last_ff_row = ff['Date'].iloc[-1]
last_df_row = df[df['Date']==last_ff_row].index.values.astype(int)[0]

first_df_row=df['Date'].iloc[0]
first_ff_row = ff[ff['Date']==first_df_row].index.values.astype(int)[0]

ff = pd.DataFrame(ff.loc[first_ff_row:])
df = pd.DataFrame(df.loc[:last_df_row])

################################################################

#Now that we have the same sized Dataframes 
#in the same order combine them together

################################################################



'''