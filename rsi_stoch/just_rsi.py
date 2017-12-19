# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 18:50:30 2017

@author: 63669
"""

from datetime import datetime
import pandas as pd
#import pandas_datareader.data as web
import requests
import json
key        = 'TJLL4VNF9L2C2CNT'
objectlist = []
log = open('log.txt','w')
log.write(str(datetime.now()))
log.write('\n')
log = open('log.txt','a')

f = open('output.txt','w')
f.write(str(datetime.now()))
f.write('\n')
f.write('=========================================')
f = open('output.txt','a')
def get_symbols():
    nasdaq = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NASDAQ&render=download")
    nyse   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NYSE&render=download")
    amex   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=AMEX&render=download")
    symbols_combined   = pd.concat([nasdaq, nyse, amex])
    symbol_list = symbols_combined.sort_values('MarketCap').Symbol.tail(500).values
    
    return symbol_list


def get_stoch(symbol): #get stochastic oscillator data

    try:
        url='https://www.alphavantage.co/query?function='\
        'STOCH&symbol='+str(symbol.strip()).lower()+'&interval=daily&outputsize=compact&apikey='+key
        log.write(url+'\n')
        u         = requests.get(url)
        data      = json.loads(u.text)
        stochdata = data['Technical Analysis: STOCH']
        s_dataset = {}
        for element in data['Technical Analysis: STOCH']: #get the data from this section
            x     = stochdata[element] #get the right data points and add to dictionary
            slowk = float(x['SlowK'])
            slowd = float(x['SlowD'])
            s_dataset[element] = [slowk,slowd]
            
        #covnert to pandas dataframe
        stoch_df         = pd.DataFrame.from_dict(s_dataset,orient='index')
        stoch_df.columns = ['SlowK','SlowD']
        return(stoch_df.head(1))
    
    except Exception:
        log.write('error getting stoch data for %s \n' %symbol)
        print('error in stoch for %s' %symbol) 
  
    
def get_RSI(symbol):
    try:
        url = 'https://www.alphavantage.co/query?function=RSI&symbol='+str(symbol.strip()).lower()+\
              '&interval=daily&time_period=10&series_type=close&apikey='+key
        log.write(url+'\n')
        u         = requests.get(url)
        data      = json.loads(u.text)
        rsidata   = data['Technical Analysis: RSI']
        s_dataset = {}
        
        for element in data['Technical Analysis: RSI']:
            x     = rsidata[element]
            rsi   = float(x['RSI'])
            s_dataset[element] = [rsi]
            
        rsi_df    = pd.DataFrame.from_dict(s_dataset,orient = 'index')
        rsi_df.columns = ['RSI']
        return rsi_df.head(1)
    except Exception:
        log.write('error getting rsi data for %s \n' %symbol)
        print('error getting rsi data for %s' %symbol)
        return None
    
           
class ranking():
    
    def __init__(self,symbol,date,sk,sd,rsi):
        self.symbol      = symbol
        self.date        = date
        self.SK          = sk
        self.SD          = sd
        self.RSI         = rsi

    def __str__(self):
        return str(self.symbol)    + '|' + str(self.date) + '|' + str(self.SK)+'|' + str(self.SD) + '|' + str(self.RSI)

symbols = get_symbols()

for symbol in symbols:
    try:
        print('Begin Processing %s' %symbol, datetime.now())
        print()
        print('Retrieving historical data',datetime.now())
        print()
        
        print('Retrieving Stochastic Data',datetime.now())
        print()
        stoch = get_stoch(symbol)
        print('Retrieving RSI data',datetime.now())
        print()
        rsi   = get_RSI(symbol)
        print('Creating variables',datetime.now())
        print()
        ticker = symbol
        date   = stoch.index[0]
        sd     = stoch.get_value(stoch.index[0],'SlowD')
        sk     = stoch.get_value(stoch.index[0],'SlowK')
        r      = rsi.get_value(rsi.index[0],'RSI')
        a = ranking(ticker,date,sk,sd,r)
        objectlist.append(a)
        print(str(objectlist[-1]))
        f.write(str(objectlist[-1])+'\n')
    except Exception:
        print('Error creating week object for %s'%symbol)
        log.write('error creating week object for %s \n' %symbol)
        print()
        continue
            

print('finished processing',datetime.now())    
print()

        


