# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 15:37:49 2017

@author: 63669
"""
import pandas as pd
import pandas_datareader.data as web
import datetime as datetime
import math

errorlist     = []
all_etfs_list = []

def import_listings():
    try:
        etfs      = []
        with open('stash.csv','r') as f:
            for line in f.readlines():
                etfs.append(line.strip().replace('  ','').split(','))
        f.close()
        
        return(etfs)
        
    except Exception:
        print('Error importing yaml')
        errorlist.append(['error importing yaml',Exception])
        return None

def add_ma(data):
    
    closes = data['Adj Close']
    MA50   = closes.rolling(50).mean()
    MA200  = closes.rolling(200).mean()
    
    data['50 Day MA'] = MA50
    data['200 Day MA'] = MA200
    
    return data

def returns(closes):
    Returns = []
    try:
        Return30Day   = abs(closes[-20]-closes[0])/(closes[-20])
        Returns.append("{0:.2f}%".format(Return30Day))
        Return6Months = abs(closes[-126]-closes[0])/(closes[-126])
        Returns.append("{0:.2f}%".format(Return6Months))
        Return1Year   = abs(closes[-252]-closes[0])/(closes[-252])
        Returns.append("{0:.2f}%".format(Return1Year))            
        Return3Year   = abs(closes[-252*3]-closes[0])/(closes[-252*3])
        Returns.append("{0:.2f}%".format(Return3Year))
        Return5Year   = abs(closes[-252*5]-closes[0])/(closes[-252*5])
        Returns.append("{0:.2f}%".format(Return5Year))
        Return10Year  = abs(closes[-252*10]-closes[0])/(closes[-252*10])
        Returns.append("{0:.2f}%".format(Return10Year))
        return Returns
    
    except Exception:
        x = len(Returns)
        i=0
        for i in range(6-x):
            Returns.append('Na')
            i+=1
            
        return Returns
    
def get_summary(returns,names):
    
    Month1 = pd.Series({'1 Month' :[ret[0] for ret in returns]})
    Month6 = pd.Series({'6 Month' :[ret[1] for ret in returns]})
    Year1  = pd.Series({'1 Year'  :[ret[2] for ret in returns]})
    Year3  = pd.Series({'3 Years' :[ret[3] for ret in returns]})
    Year5  = pd.Series({'5 Years' :[ret[4] for ret in returns]})
    Year10 = pd.Series({'10 Years':[ret[5] for ret in returns]})
        
    rets = pd.concat([Month1,Month6,Year1,Year3,Year5,Year10],axis=1)
    Summary = pd.DataFrame(rets,index=names)
        
    
    return Summary
        
def excel_writer(data,summary,symbols):

        fname       = datetime.datetime.now().strftime('%Y-%m-%d')+'.xlsx'
        sheet_names = ['Summary']
        writer      = pd.ExcelWriter(fname, engine='xlsxwriter')
        workbook    = writer.book

        format1     = workbook.add_format({'num_format': '0.00'})   #formats decimals to 2 places
       
        for symbol in symbols:
            sheet_names.append(symbols[0].replace('Ticker Symbol',''))
            
        summary.to_excel(writer,sheet_name=sheet_names[0])
    
        j=1   
        for j in range(len(sheet_names)-1):
            data.to_excel(writer,sheet_name=sheet_names[j])
            
            closes    = data['Adj Close'].values
            mincloses = math.floor(min(closes))
            workbook  = writer.book
            format1   = workbook.add_format({'num_format': '0.00'})   #formats decimals to 2 places
            worksheet = writer.sheets[sheet_names[j]] #stochastic oscillator sheet            
        
            worksheet.set_column('B:J',20,format1) #column formatting
        
            # Create a chart object.
            chart      = workbook.add_chart({'type': 'line'})
            max_row    =len(data) #last year of data has 252 points (change to variable input)
            categories =['Adj Closes','50 Day MA','200 Day MA' ]
            # Configure the series of the chart from the dataframe data.
            for i in range(len(categories)):
                col = i + 5 #starting at column 6
                chart.add_series({
                        'name'      : [sheet_names[i], 0, col],
                        'categories': [sheet_names[i], 1, 0,   max_row, 0],
                        'values'    : [sheet_names[i],1, col, max_row, col],
                        'line'      : {'width':0.25}, 
                        })
            # Configure the chart axes.
            chart.set_x_axis({'name': 'Dates'}) #y axis has min value near min of closes
            chart.set_y_axis({'name': 'Closing Price', 'min': mincloses*0.85,'major_gridlines': {'visible': False}})
        
            worksheet.insert_chart('M2', chart) #add to current worksheet

            # Close the Pandas Excel writer and output the Excel file.
            writer.save()
            j+=1
            print(fname)
            return(fname) 

def get_data(symbol):
    try:
        month       = 21 #average days in a month
        year        = 252
        data        = web.DataReader(symbol,'yahoo',retry_count = 10)
        data.drop('Volume',axis=1,inplace = True)
        start_date        = data.index[0]
        end_date          = data.index[-1]
        data              = add_ma(data)[199:]
        data['1 Month' ]  = data['Adj Close'].pct_change(month)
        data['6 Months']  = data['Adj Close'].pct_change(6*month)
        data['1 Year'  ]  = data['Adj Close'].pct_change(year)
        data['3 Years' ]  = data['Adj Close'].pct_change(3*year)
        data['5 Years' ]  = data['Adj Close'].pct_change(5*year)
        data['10 Years']  = data['Adj Close'].pct_change(10*year)
        returns           = data.tail(1)
        print(returns)
        #labels      = ['1 Month', '6 Months', '1 Year', '3 Years', '5 Years','10 Years']        
        #summary     = pd.DataFrame(return_data,columns = labels)   
        
        return(data,start_date,end_date,return_data,return_data)
        
    except Exception:
        print('error getting data!')
        return None
        

class etf():
    Name = ''
    Ticker = ''
    Returns = [] #1 Month, 1 Year, 3 Years, 5 Years, 10 Years
    Data    = []
    
    def __init__(self,Name,Ticker):
        
        self.Name   = Name
        self.Ticker = Ticker.replace(' ','')
        
        #get_data(self)
            
    def __str__(self):
        return self.Name + '-' + self.Ticker
    
    def excel_row(self):
        row = [self.Name,self.TTicker]
        for ret in self.Returns:
            row.append(ret)
            
        return row
    
ticker_names = import_listings()

for name,ticker in ticker_names:
    obj = etf(name,ticker)
    all_etfs_list.append(obj)

all_data    = []
all_returns = []
names       = []
retry_list  = []
for etf in all_etfs_list[:1]:
    print('Getting Data for:',etf.Ticker)
    try:
        data,start,end,return_data,Returns = get_data(etf.Ticker)
        names.append(etf.Name)
        all_data.append(data)
        all_returns.append(Returns)
    except Exception:
        print('error with:',etf.Ticker)
        retry_list.append(etf.Ticker)
        continue

fname = excel_writer(data,summary,ticker_names[0])


print(fname)
