#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 09:29:21 2018

@author: ruben.ramirez
"""

import pandas as pd
import numpy as np
import itertools
import math
import re

##Parse the file
xl = pd.ExcelFile("PL_13_june_daus.xlsx")
df = xl.parse("total")


roseta = pd.ExcelFile("rosetta.xls")
roseta = roseta.parse("total")

df = xl.parse("total")

#Get the GPU counterparts
gpu_file = 'gpu_counterparts.csv'
gpu_counterparts = pd.read_csv(gpu_file)

######## Initial Mungling ################################################

##Fill with np.nan for non existing values
df = df.replace(r'^\s+$', np.nan, regex=True)
df['Counterpart'].replace(r'^-', np.nan, regex=True, inplace = True)

#Create a GPU dictonary from the GPU_Counterpart CSV
gpu_dict={}
for x in gpu_counterparts['GPU']:
    gpu_dict[x]= gpu_counterparts[(gpu_counterparts['GPU'] == str(x))]['Counterpart'].unique()[0]

#Map it later (Some sort of Vlookup)
df['Counterpart'] = df.GPU.map(gpu_dict)

#Create a dictonary of SOC and Counterparts
soc_dict={}
for x in df['SOC'].unique():
    if len(df[(df['SOC'] == str(x))]['Counterpart'].unique()) > 0:
        soc_dict[x]= str(df[(df['SOC'] == str(x))]['Counterpart'].unique()[0])        
#Map by SOC with counterpart      
df['Counterpart'] = df.SOC.map(soc_dict)

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
high_gpu_list = ['iPhone 6s','iphone 6s' ,'iPhone 6s-','iPhone 6s+','iPhone 7','iPhone 7-','iPhone 7+','iPhone 8','iPhone 8+','iPhone 8-','iPhone 8+']

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

def get_best_freq(a,b):
    if a > b:
        return a
    else:
        return b

def get_freq(first_cpu_info, second_cpu_info):
    #Get the frequency of both CPUs
    frequency_first_cpu = int(re.findall(r'\d+', str(first_cpu_info).split('(')[1])[0])
    frequency_second_cpu = int(re.findall(r'\d+', str(second_cpu_info).split('(')[1])[0])
    biggest_freq = get_best_freq(frequency_first_cpu,frequency_second_cpu)
    return biggest_freq
    

def cpu_checker(cpu_info):
    first_cpu = str(cpu_info).split("; ")[0] 
    first_cpu_initial = first_cpu[0:1]
    if first_cpu_initial == 'A' or first_cpu_initial == 'Q':
        case_number = 1
        return case_number
    if len(str(cpu_info).split("; ")) > 1:
        #Get CPU Initials
        second_cpu = str(cpu_info).split("; ")[1] 
        second_cpu_initial = second_cpu[0:1]
        #Get frequency
        frequency = get_freq(first_cpu,second_cpu)
        if first_cpu_initial == "2" and second_cpu_initial == "2" and frequency < 2200:
            case_number = 1
            return case_number
        if first_cpu_initial == "2" and second_cpu_initial == "2" and frequency >= 2200:
            case_number = 2
            return case_number
        if first_cpu_initial == "4" or second_cpu_initial == "4":
            if frequency < 1800:
                case_number = 1
                return case_number
            if frequency >= 1800 and frequency < 2350:
                case_number = 2
                return case_number
            if frequency >= 2350:
                case_number = 3
                return case_number
        if first_cpu_initial == "6" or second_cpu_initial == "6":
            case_number = 2
            return case_number
        if first_cpu_initial == "8" or second_cpu_initial == "8":
            case_number = 2
            return case_number
        
    #If we have just one CPU
    elif len(str(cpu_info).split("; ")) <= 1:
        if len(str(cpu_info).split('(')) > 1:
            frequency = int(re.findall(r'\d+', str(cpu_info).split('(')[1])[0])
            if first_cpu_initial == "2" and frequency < 2200:
                case_number = 1
                return case_number
            if first_cpu_initial == "2" and frequency >= 2200:
                case_number = 2
                return case_number
            if first_cpu_initial == "4":
                if frequency < 1800:
                    case_number = 1
                    return case_number
                if frequency >= 1800 and frequency < 2350:
                    case_number = 2
                    return case_number
                if frequency >= 2350:
                    case_number = 3
                    return case_number
            if first_cpu_initial == "8":
                case_number = 2
                return case_number 
            if first_cpu_initial == "6":
                case_number = 2
                return case_number
        
def add_cpu_families(row):
    get_case = cpu_checker(row)
    if get_case == 1:
        return "LOW-CPU"
    if get_case == 2:
        return "MID-CPU"
    if get_case == 3:
        return "HIGH-CPU"
    

df['CPU_FAM'] = df['CPU'].apply(add_cpu_families)

df.isnull().sum()
    

####################### FIND POSSIBLE FAMILIES #######################################


#Changes Below Iphone4s for easier parsing and more coherent naming.
df.replace('Below iPhone 4s', 'iPhone 4', inplace=True)
df.fillna('-', inplace=True)
df.replace('nan','-', inplace=True)
df['new_families'] = df['Counterpart'] + "/" + df['RAM_FAM'] + "/" + df['GPU_FAM'] + "/" + df['CPU_FAM']

def parse_new_fams(row):
    if type(row) == str:
        if len(row.split('/')) > 1:
            groups = row.split('/')
            counter = groups[0][0] + groups[0][7:]
            ram = groups[1][0] 
            gpu = groups[2][0] 
            cpu = groups[3][0] 
            result = str(counter) + ': ' + str(ram) + '/' + str(gpu) + '/' + str(cpu)
            return result

df['family'] = df['new_families'].apply(parse_new_fams)
#Drop new families, not necesary
df = df.drop(columns=['new_families'])    

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

df.isnull().sum()
len(df['SOC'].value_counts())



writer = pd.ExcelWriter('pl_ultimate_updated.xlsx')
df.to_excel(writer,'total')
writer.save()

        