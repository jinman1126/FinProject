# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 05:17:52 2017

@author: 63669
"""
import pandas as pd
import datetime
from datetime import timedelta as td

class Process_Data():
    
    Symbol    = '' 
    DF        = pd.DataFrame()
    StartDate = ''
    EndDate   = ''
    outputdf  = pd.DataFrame()
    
    
    def __init__(self,S,DF):
        self.Symbol   = S
        self.DF       = DF
        self.StartDate = self.DF.index[0]
        self.EndDate   = self.DF.index[-1]
        
        self.BackTest(self.Symbol,self.DF)
        
    def BackTest(self,S,DF):
        
        errorlist = []
         
        #########################################################
        
        #Step 1: prepare dates
        #organize data by start of month, end of month
        
        #########################################################
        
        try:
            startmonth = int(self.StartDate.strftime('%m')) + 1
            endmonth   = int(self.EndDate.strftime('%m')) - 1
        
            startyear  = int(self.StartDate.strftime('%Y'))
            endyear    = int(self.EndDate.strftime('%Y'))
        
        #handle end of year cases
            if startmonth == 12:
                startmonth = 1
                startyear +=1
        
            if endmonth   ==  0:
                endmonth   = 12
                endyear   -=  1
        
        except Exception:
            errorlist.append(['Step 1 error'])
            print(errorlist)
        
        ##########################################################
        
        #Step 2: Compile a list of starting dates for each month!
        
        ##########################################################
        
        try:
            Datelist   = self.DF.index
            YM         = set()
            BeginDates = []
            
            for date in Datelist:
                ym = int(date.strftime('%Y%m'))
                if ym not in YM:
                    BeginDates.append(date)
                    YM.add(ym)
                
        except Exception:
            errorlist.append('Step 2 error')
            print(errorlist)
            
        ##########################################################
        
        #Step 3: get values for each date and determine buy/sells
        
        ##########################################################
        try:
            i=1
            actions         = []
            Profit_Loss     = []
            Returns         = []   
            EndDates        = []
            StartPrice      = []
            EndPrice        = [] 
            x               = len(BeginDates)
            '''
            action0         = self.DF.get_value(BeginDates[0],'Actions')
            if   action0 == 0:
                actions.append('Hold')
            else:
                actions.append('Buy')
                
            StartPrice.append(self.DF.get_value(BeginDates[0],'Adj Close'))
            Returns.append('Nan')
            Profit_Loss.append('Nan')
            EndPrice.append('Nan')
            EndDates.append(BeginDates[1])
            '''
            for i in range(x-1):
                
                action     = self.DF.get_value(BeginDates[i],'Actions')
                prevaction = self.DF.get_value(BeginDates[i-1],'Actions')
                
                if   action == 1 and prevaction == 1:
                    actions.append('Hold')
                elif action == 1 and prevaction == 0:
                    actions.append('Buy')
                elif action == 0 and prevaction == 0:
                    actions.append('Hold')
                elif action == 0 and prevaction == 1:
                    actions.append('Sell')
            
                startprice      = self.DF.get_value(BeginDates[i],'Adj Close')   
                endprice        = self.DF.get_value(BeginDates[i+1],'Adj Close')
                returns         = (endprice - startprice)/startprice
                profit_loss     =  endprice - startprice
                Profit_Loss.append(profit_loss)
                Returns.append(returns)
                StartPrice.append(startprice)
                EndPrice.append(endprice)
                EndDates.append(BeginDates[i+1])
                i+=1
                
        except Exception:
            errorlist.append('Step 3 error')
            print(errorlist)
            
        ##########################################################
        
        #Step 4: Create output data and return
        
        ##########################################################
        
        try:
            BeginDates  = pd.Series(BeginDates)
            actions     = pd.Series(actions)
            Profit_Loss = pd.Series(Profit_Loss)
            Returns     = pd.Series(Returns)
            EndDates    = pd.Series(EndDates)
            StartPrice  = pd.Series(StartPrice)
            EndPrice    = pd.Series(EndPrice)
            outputdf    = pd.DataFrame(
                                       { 'Dates'         : BeginDates
                                        ,'Actions'       : actions
                                        ,'P/L'           : Profit_Loss
                                        ,'Monthly Return': Returns
                                        ,'Start Price'   : StartPrice
                                        ,'End Price'     : EndPrice
                                        ,'End Dates'     : EndDates}
                                        ,columns = ['Dates'
                                                   ,'End Dates'
                                                   ,'Actions'
                                                   ,'Start Price'
                                                   ,'End Price'
                                                   ,'P/L'
                                                   ,'Monthly Return']
                                       ) 
            print(outputdf)
            self.outputdf = outputdf
            return(outputdf)                         
    
        except Exception:
            errorlist.append('Step 4 error')
            print(errorlist)
            
        
            
testfile = 'AAPL.csv'
DF       = pd.read_csv(testfile,sep=',',index_col=[0],parse_dates=True)
S        = 'AAPL'

x = Process_Data(S,DF)

                        
                    
                    
            
            
            
        
        
        
        
        
    
    