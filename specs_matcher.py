#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 28 11:03:08 2018

@author: macintosh
"""
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
import numpy as np

xl = pd.ExcelFile("compiled_pl_5_6_18_aspectratio.xlsx")
df = xl.parse("total")

#GPPA file to compare 
xl_gppa = pd.ExcelFile("GPPA_FILTERED.xls")
df_gppa = xl_gppa.parse("GPPAFilteredReport")


existing_in_studio = pd.DataFrame()     
for x , df_row in df.iterrows():
    for i, row in df_gppa.iterrows():
        if(pd.notna(row['name']) and pd.notna(df_row['name'])):
            match_ratio = fuzz.partial_ratio(str(df_row['name']), str(row['name']))
            print ("Index: " + str(i) +  " " +  str(df_row['name']) + " on row: " + str(row['name']))
            if match_ratio > 70:
                
                print(str(match_ratio))
                existing_in_studio = existing_in_studio.append(pd.DataFrame(df[df['name'] == df_row['name']]), ignore_index=True)   
                

writer = pd.ExcelWriter('existingjogpartial.xlsx')
existing_in_studio.to_excel(writer,'total')
writer.save()
            