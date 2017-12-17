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

f = open('rsi//output.txt','w')
f.write(str(datetime.now()))
f.write('\n')
f.write('=========================================')
f = open('rsi//output.txt','a')
def get_symbols():
    nasdaq = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NASDAQ&render=download")
    nyse   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NYSE&render=download")
    amex   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=AMEX&render=download")
    symbols_combined   = pd.concat([nasdaq, nyse, amex])
    symbol_list = symbols_combined.sort_values('MarketCap').Symbol.tail(500).values
    
    return symbol_list

def get_weeks(df):
    Mondaylist = []
    Fridaylist = []
    get_list   = []
    for index,day in enumerate(reversed(df.index)):
        if day.weekday() == 0:
            Mondaylist.append(day)
            get_list.append(index+4)
            
        if index in get_list:
            Fridaylist.append(day)
    if (Fridaylist[0]-Mondaylist[0]).days <= 0:
        Fridaylist.pop(0)        
        
    if (Fridaylist[-1]-Mondaylist[-1]).days < 0:
        Mondaylist.pop(-1)

    return Mondaylist,Fridaylist

def get_last_100_days(symbol):
    
    try:
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY'\
               '&symbol=' + str(symbol) + '&outputsize=full&apikey=' + key + '&datatype=csv'

        df = pd.read_csv(url,header = 0, index_col = [0], sep = ',', parse_dates = [0])
        smalldf = df.head(500)
        Mondaylist,Fridaylist = get_weeks(smalldf)
        
        return smalldf,Mondaylist,Fridaylist
    except Exception:
        print('error retrieving last 100 days of data for %s'%symbol)
        return None

def get_stoch(symbol): #get stochastic oscillator data

    try:
        url='https://www.alphavantage.co/query?function='\
        'STOCH&symbol='+str(symbol)+'&interval=daily&outputsize=compacto/query?function=STOCH&symbol=AAPL&interval=daily&outputsize=compact&apikey=TJLL4VNF9L2C2CNT&apikey='+key
        
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
        
        return(stoch_df.head(500))
    
    except Exception:
        print('error in stoch') 
  
def get_ma(symbol):
    try:
        times    = [15,60]
        datasets = []
        for time in times:
            url = 'https://www.alphavantage.co/query?function=EMA&symbol='+str(symbol)+\
                '&interval=daily&time_period='+str(time)+'&series_type=close&apikey=' + key
            #print(url)
            u         = requests.get(url)
            data      = json.loads(u.text)
            ma_data   = data['Technical Analysis: EMA']
            s_dataset = {}
            
            for element in data['Technical Analysis: EMA']:
                x     = ma_data[element]
                ema   = float(x['EMA'])
                s_dataset[element] = [ema]
            datasets.append(s_dataset)
            
        for k,v in datasets[1].items():
            datasets[0][k].extend(v)
            
        ma_df     = pd.DataFrame.from_dict(datasets[0],orient = 'index')
        ma_df.columns = ['15EMA','60EMA']
        return(ma_df.head(500))
        
    except Exception:
        print('error getting ma data for %s'%symbol)
        return None
    
def get_RSI(symbol):
    try:
        url = 'https://www.alphavantage.co/query?function=RSI&symbol='+str(symbol)+\
              '&interval=daily&time_period=10&series_type=close&apikey='+key
        #print(url)      
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
        
        return rsi_df.head(500)
    except Exception:
        print('error getting rsi data for %s' %symbol)
        return None
    
           
class ranking():
    
    def __init__(self,symbol,date,bp,sp,rsi):
        self.symbol      = symbol
        self.date        = date
        self.BuyPrice    = bp
        self.SellPrice   = sp
        self.RSI         = rsi

    def __str__(self):
        return str(self.symbol)    + '|' + str(self.date) + '|' + str(self.BuyPrice) +'|' \
              +str(self.SellPrice) + '|' + str(self.RSI)

symbols = get_symbols()

for symbol in symbols:
    try:
        print('Begin Processing %s' %symbol, datetime.now())
        print()
        print('Retrieving historical data',datetime.now())
        print()
        df,Mondaylist,Fridaylist = get_last_100_days(symbol)
        '''
        print('Retrieving Stochastic Data',datetime.now())
        print()
        stoch = get_stoch(symbol)
        
        print('Retrieving MA data',datetime.now())
        print()
        ma    = get_ma(symbol)
        '''
        print('Retrieving RSI data',datetime.now())
        print()
        rsi   = get_RSI(symbol)
        
        i=0
        print('Creating variables',datetime.now())
        print()
        for day in Mondaylist:
            daydate = day.strftime('%Y-%m-%d')
            ticker = symbol
            date   = daydate
            bp     = df.get_value(day,'open')
            sp     = df.get_value(Fridaylist[i],'close')
            r      = rsi.get_value(daydate,'RSI')
            a = ranking(ticker,date,bp,sp,r)
            objectlist.append(a)
            i+=1
            print(str(objectlist[-1]))
            f.write(str(objectlist[-1])+'\n')
    except Exception:
        print('Error creating week object for %s'%symbol)
        print()
        continue
            

print('finished processing',datetime.now())    
print()

        


