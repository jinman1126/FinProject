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
f = open('rsi_stoch_ma//output.txt','w')
f.write(str(datetime.now()))
f.write('\n')
f.write('=========================================\n')
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
            get_list.append(index+2)
            
        if index in get_list:
            Fridaylist.append(day)
            
    if (Fridaylist[0]-Mondaylist[0]).days <= 0:
        Fridaylist.pop(0)        
        
    if (Fridaylist[-1]-Mondaylist[-1]).days < 0:
        Mondaylist.pop(-1)

    return Mondaylist,Fridaylist

def get_last_100_days(symbol,retry_count):
    
    try:
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY'\
               '&symbol=' + str(symbol) + '&outputsize=full&apikey=' + key + '&datatype=csv'

        df = pd.read_csv(url,header = 0, index_col = [0], sep = ',', parse_dates = [0])
        smalldf = df.head(500)
        Mondaylist,Fridaylist = get_weeks(smalldf)
        
        return smalldf,Mondaylist,Fridaylist
    except Exception:
        retry_count +=1
        print('Retry count: %d' %retry_count)
        if retry_count <= 5:
            get_last_100_days(symbol,retry_count)
        else:
            
            print('error retrieving last 100 days of data for %s'%symbol)
            return None

def get_stoch(symbol,retry_count): #get stochastic oscillator data

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
        retry_count +=1
        print('Retry count: %d' %retry_count)
        print(url)
        if retry_count <= 5:
            get_stoch(symbol,retry_count)
        else:
            print('error in stoch')
            return None
  
def get_ma(symbol,retry_count):
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
        retry_count +=1
        print('Retry count: %d' %retry_count)
        print(url)
        if retry_count <= 5:
            get_ma(symbol,retry_count)
        else:
            print('error getting ma data for %s'%symbol)
            return None
    
def get_RSI(symbol,retry_count):
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
        retry_count +=1
        print('Retry count: %d' %retry_count)
        print(url)
        if retry_count <= 5:
            get_RSI(symbol,retry_count)
        else:
            print('error getting rsi data for %s' %symbol)
            return None
             
class ranking():
    
    def __init__(self,symbol,date,bp,sp,stoch,ma,rsi):
        self.symbol      = symbol
        self.date        = date
        self.BuyPrice    = bp
        self.SellPrice   = sp
        self.Stochastic  = stoch
        self.MA          = ma
        self.RSI         = rsi
        self.Score       = 0
        self.BuyDecision = 0
        self.Profit      = 0
        slowk  = self.Stochastic[0]
        slowd  = self.Stochastic[1]
        if slowk <=20 and slowd <= 20:
            stoch_ranking = 1-((slowk+slowd)/200)
            self.Score += stoch_ranking
        else:
            stoch_ranking = 0
        ma15 = self.MA[0]
        ma60 = self.MA[1]
        ma_ranking = (self.BuyPrice/ma15 + self.BuyPrice/ma60)/2
        self.Score += ma_ranking
        if self.RSI <= 30:
            rsi_ranking = 1-(self.RSI/100)
            self.Score += rsi_ranking
        
    def __str__(self):
        return str(self.symbol)    + '|' + str(self.date) + '|' + str(self.BuyPrice) +'|' \
              +str(self.SellPrice) + '|' + str(self.Score)

symbols = get_symbols()

for symbol in symbols:
    try:
        retry_count = 0 
        print('Begin Processing %s' %symbol, datetime.now())
        print()
        print('Retrieving historical data',datetime.now())
        print()
        df,Mondaylist,Fridaylist = get_last_100_days(symbol,retry_count)
        
        print('Retrieving Stochastic Data',datetime.now())
        print()
        stoch = get_stoch(symbol,retry_count)
        
        print('Retrieving MA data',datetime.now())
        print()
        ma    = get_ma(symbol,retry_count)
        
        print('Retrieving RSI data',datetime.now())
        print()
        rsi   = get_RSI(symbol,retry_count)
        
        i=0
        print('Creating variables',datetime.now())
        print()
        for day in Mondaylist:
            daydate = day.strftime('%Y-%m-%d')
            ticker = symbol
            date   = daydate
            bp     = df.get_value(day,'open')
            sp     = df.get_value(Fridaylist[i],'close')
            st     = [stoch.get_value(daydate,'SlowK'),stoch.get_value(daydate,'SlowD')]
            m      = [ma.get_value(daydate,'15EMA'),ma.get_value(daydate,'60EMA')]
            r      = rsi.get_value(daydate,'RSI')
            a = ranking(ticker,date,bp,sp,st,m,r)
            objectlist.append(a)
            i+=1
            #print(str(objectlist[-1]))
            #print()
       
        print('writing data for %s' %symbol)
        print()
        with open('rsi_stoch_ma//output.txt','a') as f:        
            for obj in objectlist:
                f.write(str(obj)+'\n')
            f.close()
            objectlist.clear()
    except Exception:
        print('Error with week for %s'%symbol)
        print()
        continue
            

print('finished processing',datetime.now())    
print()

        


