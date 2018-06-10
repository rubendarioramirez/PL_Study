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
import math
import re

##Parse the file
xl = pd.ExcelFile("DeviceList_25May2018.xlsx")
df_raw = xl.parse("Pub List Data")
#Get the GPU counterparts
gpu_file = 'gpu_counterparts.csv'
gpu_counterparts = pd.read_csv(gpu_file)
#Create a GPU dictonary
gpu_dict = gpu_counterparts.set_index('GPU').to_dict()


######## Initial Mungling ################################################

##Fill with np.nan for non existing values
df_raw = df_raw.replace(r'^\s+$', np.nan, regex=True)
df_raw['Counterpart'].replace(r'^-', np.nan, regex=True, inplace = True)

##Verifying Adreno 530
df_raw[(df_raw['SOC']=='Qualcomm MSM8996') | (df_raw['SOC']=='Qualcomm APQ8096')]['GPU'] = 'Adreno 530'
##Verifying Adreno 510
df_raw[(df_raw['SOC']=='Qualcomm MSM8994') | (df_raw['SOC']=='Qualcomm APQ8094')]['GPU'] = 'Adreno 430'
##Verifying Adreno 430
df_raw[(df_raw['SOC']=='Qualcomm APQ8076') | (df_raw['SOC']=='Qualcomm MSM8976')]['GPU'] = 'Adreno 510'

#Get missing Counterpart DF
df_nocounter = df_raw[df_raw['Counterpart'].isnull() == True]
df_counterpart = df_raw[df_raw['Counterpart'].isnull() == False]

#Now map it like in the cowboy movies        
df_nocounter['Counterpart'] = df_nocounter.GPU.map(gpu_dict)
#Concat to a new DF with more devices
df = pd.concat([df_counterpart, df_nocounter])

#Create a dictonary of GPUS and Counterparts
gpu_dict={}
for x in df_counterpart['GPU'].unique():
    if len(df_counterpart[(df_counterpart['GPU'] == str(x))]['Counterpart'].unique()) > 0:
        gpu_dict[x]=str(df_counterpart[(df_counterpart['GPU'] == str(x))]['Counterpart'].unique()[0])

gpu_dict['Qualcomm Adreno 509 (370Mhz)'] = 'iPhone 5s'
gpu_dict['Intel HD Graphics 500 (650Mhz)'] ='iPhone 6-'
gpu_dict['Intel HD Graphics 400 (600Mhz)'] ='iPhone 5s+'
gpu_dict['Intel HD Graphics 400 (640Mhz)'] ='iPhone 5s+'
gpu_dict['ARM Mali T820 (550Mhz)'] ='iPhone 5s-'
gpu_dict['3x ARM Mali G72 (800Mhz)'] ='iPhone 8'
gpu_dict['Imagination Tech PowerVR GE8320 (650Mhz)'] ='iPhone 5s+'

df['Counterpart'] = df['GPU'].map(gpu_dict)

df.isnull().sum()

#### RAM PARSING #####################################

#Variables to setup before compiling the PL
low_ram_def = 1024
mid_ram_def = 2048

#Make RAM a float type for easier parsing
df['RAM'] = pd.to_numeric(df['RAM'], errors='coerce')

# definition for the ram types above.
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

##### GPU PARSING #################################
##Create a list of GPUs per type, LOW, MID, HIGH
low_gpu_list = ['Below iPhone 4s','iPhone 4s','iPhone 4s-','iPhone 4s+','iPhone 5','iPhone 5-','iPhone 5+']
mid_gpu_list = ['iPhone 5s','iPhone 5s-','iPhone 5s+','iPhone 6','iPhone 6-','iPhone 6+']
high_gpu_list = ['iphone 6s','iPhone 6s-','iPhone 6s+','iPhone 7','iPhone 7-','iPhone 7+','iPhone 8+','iPhone 8-','iPhone 8+']

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

##### CPU PARSING #################################

def add_cpu_fam(row):
    #CPU LOW
    #[x]Contains 2x and does not contain 4x or 6x or 8x
    #[x]Contains 4x and freq is below 1800
    #[x]Does not contain 2x or 4x or 6x or 8x
    #CPU MID
    #[x]Contains 4x and freq is above [1800,2400)
    #[x]Contains 6x
    #[x]Contains 8x
    #[x]Contains 2x and does not contain 4x or 6x or 8x and freq is above 2000
    #CPU MID
    #Contains 4x and freq is above 2400 (including)
    
    bestCPU = ''
    freq = ''
    #Catch the single core
    if str(row).split("; ")[0].startswith('A') or str(row).split("; ")[0].startswith('Q'):
        result = 'LOW-CPU'
        return result
    #Catch if there are more than 2 CPUS
    if len(str(row).split("; ")) > 1:
        a = str(row).split("; ")[0][0]
        b = str(row).split("; ")[1][0]
        if a.isdigit() and b.isdigit():
            freq = int(re.findall(r'\d+', str(row).split("; ")[0].split('(')[1])[0])
            #if it's 2X
            if int(a) == 2:
                bestCPU = int(a) - int(b)
                #The other one is also 2X
                if bestCPU == 0:
                    return 'LOW-CPU'
                #The second is bigger but lower frequency
                elif int(b) > 2:
                    if freq < 1800:
                        return 'LOW-CPU'
                    else:
                        return 'MID-CPU'
            elif int(a) == 4: 
                if freq > 1800 and freq < 2400:
                    return 'MID-CPU'
                    #if it has big freq
                elif freq >= 2400:
                    return 'HIGH-CPU'
                elif freq <= 1800:
                    return 'LOW-CPU'
            #It's bigger than 4X
            elif int(a) == 6:
                return 'MID-CPU'
            elif int(a) == 8:
                return 'MID-CPU'
            
    #If just 1 CPU
    elif len(str(row).split("; ")) == 1:
        a = str(row).split("; ")[0][0] 
        if a.isdigit():
            #if it's 2X then it's low
            if int(a) == 2:
                return 'LOW-CPU'
            #If Quadcore but low Freq
            elif int(a) == 4:
                freq = int(re.findall(r'\d+', str(row).split("; ")[0].split('(')[1])[0])
                if freq <= 1800:
                    return 'LOW-CPU'
                if  freq > 1800 and freq < 2400:
                    return 'MID-CPU'
                #if it has big freq
                elif freq >= 2400:
                    return 'HIGH-CPU'
            #It's bigger than 4X
            elif int(a) == 6 or int(a) == 8:
                return 'MID-CPU'
            

df['CPU_FAM'] = df['CPU'].apply(add_cpu_fam)

####################### FIND POSSIBLE FAMILIES #######################################

cpu_list = list(df['CPU_FAM'].unique())
cpu_list = cpu_list[:3]

gpu_list = list(df['GPU_FAM'].unique())
gpu_list = gpu_list[:3]

ram_list = list(df['RAM_FAM'].unique())
ram_list = ram_list[:3]

possible_fam = list(itertools.product(cpu_list,gpu_list,ram_list))

#with open('family_list.csv', "w") as output:
#    writer = csv.writer(output, lineterminator='\n')
#    for val in possible_fam:
#        writer.writerow([val])

#Create a new cell with possible families to match later.        
df['merged_cells'] = df['CPU_FAM'] + ", " + df['GPU_FAM'] + ", " + df['RAM_FAM']
#Create a dictionary of families to be matched against.
combo_to_family = {'{}-CPU, {}-GPU, {}-RAM'.format(c, g, r): 'Family {}'.format(i)
for i, (c, g, r) in enumerate(itertools.product(('LOW', 'MID', 'HIGH'), repeat=3), 1)}

def match_list(row):
    fam_list = ""
    tomatch = row
    result = combo_to_family.keys()

    for row in result :
        fam_list = combo_to_family.get(tomatch, np.nan)
    
    return fam_list

##Apply the function.
df['family_class'] = df['merged_cells'].apply(match_list)
#Drop the possible families, no need anymore.
df = df.drop(columns=['merged_cells'])

df['family_class'].value_counts()

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

#################### OUPUT THE NEW FILE ##################
    
writer = pd.ExcelWriter('pl_9june.xlsx')
df.to_excel(writer,'total')
writer.save()

        