#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 13:44:02 2018

@author: macintosh
"""


import pandas as pd

##Parse the file
xl = pd.ExcelFile("DeviceList_25May2018.xlsx")
df = xl.parse("Pub List Data")

#################### Get the real devices to test based on their revenue Share.
devicesToTest = pd.DataFrame()
for x in range(0,22): 
    maxRev = float(df[df['family_class'] == "Family "+ str(x)]['Revenue Share'].max() )
    toTest = df[df['Revenue Share'] == maxRev]
    devicesToTest = devicesToTest.append(pd.DataFrame(toTest), ignore_index=True)
    
    
writer = pd.ExcelWriter('toTest.xlsx')
devicesToTest.to_excel(writer,'total')
writer.save()
            