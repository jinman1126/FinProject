# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 20:32:42 2017

@author: 63669
"""

import pandas
import pandas_datareader.data as web
from pandas_datareader.famafrench import get_available_datasets

#print(get_available_datasets())
ff = web.DataReader('F-F_Research_Data_Factors_daily','famafrench')
print(ff[0]['RF'])