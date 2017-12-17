# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 18:38:39 2017

@author: 63669
"""
import pandas as pd
import pandas_datareader.data as web
from datetime import datetime
from datetime import timedelta

errorlist = []

class etf_data():
    Years = []

    def __init__(self,Years):
        
        etfs    = pd.read_csv("http://www.nasdaq.com/investing/etfs/etf-finder-results.aspx?download=Yes")
        symbols = etfs.Symbol[etfs.LastSale < 100].values[0:2]
        
        for symbol in symbols:
        
            df     = self.get_data(symbol,year)
            if df == 0:
                print('Finished with %s' %symbol)
                #print(df)
                continue

            else: 
                print(df)
                #report = self.summary(df,Years)
        #for symbol in symbols:
            
            #try:
                #df     = self.get_data(symbol,Years)
                #report = self.summary(df,self.Years)
            
            #except Exception:
                #errorlist.append(['Error in main',symbol])
                #continue
    
    def get_data(self,symbol,Years):
        
        try:
            start  = (datetime.now() - timedelta(days=252*Years)).strftime('%Y-%m-%d')
            end    = (datetime.now() - timedelta(days=        1)).strftime('%Y-%m-%d')
            f      = web.DataReader(symbol.strip(), 'yahoo', start, end).dropna(axis=0)
            start  = f.index[0]
            length = len(f.index)
            
            if length <= 252*Years:
                return(0)
            else:
                return(f)
            
        except Exception:
            errorlist.append(['Get_Data Error',symbol])
            return(None)
    '''        
    def summary(self,df,Years):
        
        try:
            df['Net Returns']
    '''    
if __name__ == "__main__":
    years = [1,3,5,10,15]
    for year in years:
        
        data = etf_data(year)       
        print(data)
            