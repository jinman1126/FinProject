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
import time
key        = 'TJLL4VNF9L2C2CNT'
objectlist = []
log = open('log.txt','w')
log.write(str(datetime.now()))
log.write('\n')
log = open('log.txt','a')

f = open('output.txt','w')
f.write(str(datetime.now()))
f.write('\n')
f.write('=========================================\n')
f = open('output.txt','a')

def email_send(file):
    
    import smtplib #each of these are used to read different types of emails
    import mimetypes #I send out excel, csv, png, and text
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText
    
    emailfrom = 'python.test.jmixv3@gmail.com'
    pw = 'Tucker05'    

    msg = MIMEMultipart() #define each part of our email
    msg["From"] = emailfrom
    msg["To"] = 'jeremy.inman13@gmail.com'
    msg["Subject"] = ' hourly update file'
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
    #server outbound port smtp 587
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(emailfrom,pw)
    server.sendmail(emailfrom, 'jeremy.inman13@gmail.com', msg.as_string())
    server.quit()
    print('file sent',datetime.now())
    print()
    
def get_stoch(symbol): #get stochastic oscillator data

    try:
        print(symbol)
        link ='https://www.alphavantage.co/query?function=STOCH&symbol='+str(symbol)+'&interval=15min&outputsize=compact&apikey='+key 
        log.write(link+'\n')
        u         = requests.get(link)
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
        print('got stoch')
        return(stoch_df.head(1))
    
    except Exception:
        log.write('error in stoch for %s \n' %symbol)
        print('error in stoch') 
  
    
def get_RSI(symbol):
    try:
        url = 'https://www.alphavantage.co/query?function=RSI&symbol='+str(symbol)+\
              '&interval=15min&time_period=10&series_type=close&apikey='+key
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

while True:
    symbols = []
    
    with open('symbols.txt','r') as s:
        for line in s.readlines():
            symbols.append(line)
            
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
            log.write('Error creating week object for %s \n' %symbol)
            print()
            continue
                
    f.close()
    print('finished processing',datetime.now())    
    print()
    print('sending file', datetime.now())
    print()
    email_send('output.txt')
    time.sleep(45*60)
            
    
    
