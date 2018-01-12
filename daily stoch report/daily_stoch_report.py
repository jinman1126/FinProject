# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 19:20:44 2018

@author: 63669
"""

import pandas as pd
from datetime import datetime,timedelta
#import pandas_datareader.data as web

settings = {'period'           :'1min'
           ,'numberofcompanies':100
           ,'return'           :5
           ,'emailsend'        :1
           }


key        = 'TJLL4VNF9L2C2CNT'
mailinglist = ['jeremy.inman13@gmail.com','dyaeger0624@hotmail.com']
datalist  = []
faillist  = []
allvalues = []
top5list  = []

periods = 5 
today   = datetime.now().strftime('%Y-%m-%d')

tradingday_value = 365/250
tradingdays      = int(periods*14*tradingday_value)

startdate        = (datetime.now() - timedelta(days=tradingdays)).strftime('%Y-%m-%d')

###############################################################################

#defaults

###############################################################################
stoch_period = 14
rsi_default  = 14

###############################################################################

#define class to handle getting the data

###############################################################################
def find_data(symbol):
    for data in datalist:
        if str(data.Name).lower() == str(symbol).lower():
            return str(data)
        
        

class data(): 
    
    def __init__(self,name):
        self.Name = name.strip()
        
        try:
            
            url = str( 'https://www.alphavantage.co/query?'
                      +'function=TIME_SERIES_INTRADAY'
                      +'&symbol=' + str(symbol)
                      +'&interval='+str(settings['period'])
                      +'&outputsize=full&apikey=' + key + '&datatype=csv')

            df = pd.read_csv(url,header = 0, index_col = [0], sep = ',', parse_dates = [0])            
            df = df.reindex(index=df.index[::-1])            
            df['50MA' ] = df['close'].rolling(50).mean()
            df['200MA'] = df['close'].rolling(200).mean()
            df['min'  ] = df['low'      ].rolling(window=stoch_period,center=False).min()
            df['max'  ] = df['high'     ].rolling(window=stoch_period,center=False).max()
            df['%K'   ] = 100*(df['close'].shift(1) - df['min'])/(df['max']-df['min'])
            df['%D'   ] = df['%K'].rolling(3).mean()
            self.K = df['%K'][-1]
            self.D = df['%D'][-1]   
            self.AverageVolume = int(df['volume'].mean())
            self.MA50          = df['50MA'  ][-1]
            self.MA200         = df['200MA' ][-1]
            self.LastClose     = df['close'][-1]
            
        except Exception:
            print('Error with ' + self.Name)
            
            self.K = 'na'
            self.D = 'na'
            self.AverageVolume = 'na'
            self.MA50 = 'na'
            self.MA200 = 'na'
            self.LastClose = 'na'
            faillist.append(self.Name)
        
    def __str__(self):
        
        return self.Name + '|' + str(self.K) + '|' + str(self.D) + '|' + str(self.MA50) + '|' + str(self.MA200) + '|' + str(self.LastClose) + '|' + str(self.AverageVolume)

def get_universe():
    
    #symbols_by_industry = {}
    
    nasdaq = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NASDAQ&render=download")
    nyse   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=NYSE&render=download")
    amex   = pd.read_csv("http://www.nasdaq.com/screening/companies-by-region.aspx?exchange=AMEX&render=download")
    df     = pd.concat([nasdaq, nyse, amex])
    
    symbol_list   = df.sort_values('MarketCap').Symbol.tail(settings['numberofcompanies']).values
    #industry_list = df.sort_values('Industry' ).Industry.values
    
    return(symbol_list)

symbols = get_universe()
#symbols = ['aapl','tsla']


for symbol in symbols:
    
    D = data(symbol)
    print(str(D))
    
    lis = str(D).split('|')
    allvalues.append(lis)

    if D.D != 'na':
        datalist.append(D)
    
while len(faillist) > 0:
    for num,fail in enumerate(faillist):
        D = data(fail)
        print(str(D))
        
        list = str(D).split('|')
        allvalues.append(lis)
        
        if D.D != 'na':
            datalist.append(D)
            faillist.pop(num)
        

ranked = sorted(allvalues, key = lambda x: (x[1],x[2]))[:settings['return']]

for top5 in ranked:
    symbol = top5[0]
    data   = find_data(symbol)
    top5list.append(data)
    
print(ranked)
fname = 'report_'+today+'.txt'

with open(fname,'w') as f:
    f.write('File meant to be viewed on computer screen. Formatting may not be mobile friendly\n')
    f.write('Symbol  |    %K   |   %D   |   50   |   200   |  Last Close   |   Volume\n')    
    f.write('========================================================\n')
    
    for d in top5list:
        f.write(str(d)+'\n')
    
f.close()
 

def email_send(file):
    
    import smtplib #each of these are used to read different types of emails
    import mimetypes #I send out excel, csv, png, and text
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email import encoders
    from email.mime.base import MIMEBase
    
    emailfrom = 'python.test.jmixv3@gmail.com'
    pw = 'Tucker05'    

    msg = MIMEMultipart() #define each part of our email
    msg["From"] = emailfrom
    msg["To"] = 'jeremy.inman13@gmail.com'
    msg["Subject"] = ' Daily Picks'
    #msg["Subject"] = "Your Request for " + ticker
     
        
    #encoding the file types for text, image, and other
    ctype, encoding = mimetypes.guess_type(file)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(file)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
        msg.attach(attachment)
    
    fp = open('README.DOCX', "rb")
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(fp.read())
    fp.close()    
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename='README.DOCX')
    msg.attach(attachment)
    #server outbound port smtp 587
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(emailfrom,pw)
    
    for mail in mailinglist:
        
        server.sendmail(emailfrom, mail, msg.as_string())
    server.quit()
    print('file sent',datetime.now())
    print()
   
print(fname)    
if settings['emailsend'] == 1:
    email_send(fname)