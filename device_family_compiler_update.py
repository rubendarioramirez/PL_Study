#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 09:29:21 2018

@author: ruben.ramirez
"""

import pandas as pd
import numpy as np
import itertools
import csv
import seaborn as sns
import matplotlib.pyplot as plt
import math

sns.set(style="whitegrid", color_codes=True)

##Parse the file
xl = pd.ExcelFile("DeviceList_25May2018.xlsx")
df = xl.parse("Pub List Data")

#####FIRST GROUP -- RAM PARSING #####################################
##Variables to setup before compiling the PL
low_ram_def = 1024
mid_ram_def = 2048

##Make RAM a float type for easier parsing
df['RAM'] = pd.to_numeric(df['RAM'], errors='coerce')
##This function will check each RAM type and create the new column based on your
## definition for the ram types above.
def add_ram_fam(row):
    result = ''
    if row <= low_ram_def:
        result = 'LOW-RAM'
        return result
    elif row > low_ram_def and row <= mid_ram_def:
        result = 'MID-RAM'
        return result
    elif row > mid_ram_def:
        result = 'HIGH-RAM'
        return result
    
df['RAM_FAM'] = df['RAM'].apply(add_ram_fam)

###### SECOND GROUP -- GPU PARSING #################################
##Create a list of GPUs per type, LOW, MID, HIGH
low_gpu_list = ['Below iPhone 4s','iPhone 4s-', 'iPhone 4s','iPhone 4s+','iPhone 5-', 'iPhone 5s-','iPhone 5']
mid_gpu_list = ['iPhone 5+', 'iPhone 5s+', 'iPhone 5s']
high_gpu_list = ['iPhone 6','iPhone 6+','iphone 6s','iPhone 7', 'iPhone 8+']

df.Counterpart.unique()
##This function will check for each row if the GPU is in the list above, if it's there 
##Will create the right category. If not, will return NONE
def add_gpu_fam(row):
    result = ''
    if row in low_gpu_list:
        result = 'LOW-GPU'
        return result
    elif row in mid_gpu_list:
        result = 'MID-GPU'
        return result
    elif row in high_gpu_list:
        result = 'HIGH-GPU'
        return result
    
df['GPU_FAM'] = df['Counterpart'].apply(add_gpu_fam)

###### THIRD GROUP -- CPU PARSING #################################

##Simple parsing, depending the cores the category of the CPU
def add_cpu_fam(row):
    result = ''
    if str(row).startswith('2x'):
        result = 'LOW-CPU'
        return result
    elif str(row).startswith('4x'):
        result = 'MID-CPU'
        return result
    elif str(row).startswith('8x'):
        result = 'HIGH-CPU'
        return result
    elif str(row).startswith('ARM'):
        result = 'LOW-CPU'
        return result

df['CPU_FAM'] = df['CPU'].apply(add_cpu_fam)


####################### FIND POSSIBLE FAMILIES #######################################

cpu_list = list(df['CPU_FAM'].unique())
cpu_list = cpu_list[:3]

gpu_list = list(df['GPU_FAM'].unique())
gpu_list = gpu_list[:3]

ram_list = list(df['RAM_FAM'].unique())
ram_list = ram_list[:3]

possible_fam = list(itertools.product(cpu_list,gpu_list,ram_list))

with open('family_list.csv', "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for val in possible_fam:
        writer.writerow([val])

#Create a new cell with possible families to match later.        
df['merged_cells'] = df['CPU_FAM'] + ", " + df['GPU_FAM'] + ", " + df['RAM_FAM']
#Create a dictionary of families to be matched against.
combo_to_family = {'{}-CPU, {}-GPU, {}-RAM'.format(c, g, r): 'Family {}'.format(i)
for i, (c, g, r) in enumerate(itertools.product(('LOW', 'MID', 'HIGH'), repeat=3), 1)}

def match_list(row):
    fam_list = ""
    tomatch = row
    result = pd.read_csv("family_list.csv")

    for row in result :
        fam_list = combo_to_family.get(tomatch, np.nan)
    
    return fam_list

##Apply the function.
df['family_class'] = df['merged_cells'].apply(match_list)
#Drop the possible families, no need anymore.
df = df.drop(columns=['merged_cells'])

################################################################################
#Aspect Ratio addition
def aspect_ratio(row):
    screenWidth = ""
    screenHeight = ""
    factor = ""
    result = ""
    screenWidth = int(row.split(" ")[0].split("x")[0])
    screenHeight = int(row.split(" ")[0].split("x")[1]) 
    factor = math.gcd(screenWidth, screenHeight)
    widthRatio = int(screenWidth / factor)
    heightRatio = int(screenHeight / factor)
    result = str(widthRatio) + ':' +  str(heightRatio)
    return result
    
df['aspect_ratio'] = df['Screen size'].apply(aspect_ratio)

df.aspect_ratio.unique()

#################### Get the real devices to test based on their revenue Share.
devicesToTest = pd.DataFrame()
for x in range(0,22): 
    maxRev = float(df[df['family_class'] == "Family "+ str(x)]['Revenue Share'].max() )
    toTest = df[df['Revenue Share'] == maxRev]
    devicesToTest = devicesToTest.append(pd.DataFrame(toTest), ignore_index=True)
    

#################### OUPUT THE NEW FILE
writer = pd.ExcelWriter('compiled_pl_29_5_18_aspectratio.xlsx')
df.to_excel(writer,'total')
writer.save()

writer = pd.ExcelWriter('toTest.xlsx')
devicesToTest.to_excel(writer,'total')
writer.save()
            
