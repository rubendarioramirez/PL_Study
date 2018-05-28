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

xl = pd.ExcelFile("compiled_pl_26_may_2018.xlsx")
df_tomatch = pd.read_csv("spec_list_full.csv")
df = xl.parse("total")




##Get the NO RAM Devices
no_ramselector = pd.isna(df.RAM)
df_noram = df[no_ramselector]
##Now drop them from the origial DF
df.dropna(subset=['RAM'], inplace=True)

##Match them with the device specs. Treshold ratio is 70. Could be more.
def get_match_ratio(row):
    match_ratio = fuzz.partial_ratio(str(row), df_tomatch)
    if match_ratio > 80:
        df_noram['RAM'] = df_tomatch['ram'] 
        df_noram['GPU'] = df_tomatch['gpu'] 
        df_noram['CPU'] = df_tomatch['cpu'] 
        print("Found match, updating..")
    return str(match_ratio)

df_noram.name.apply(get_match_ratio)

for index, row in df_noram.iterrows():
     match_ratio = fuzz.partial_ratio(str(row['name']), df_tomatch.model)
     if match_ratio > 80:
         print("match found")
         print(str(row['name']) + " " + str(df_tomatch.model[index]))