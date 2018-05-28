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
        

df['merged_cells'] = df['CPU_FAM'] + ", " + df['GPU_FAM'] + ", " + df['RAM_FAM']


def match_list(row):
    fam_list = ""
    tomatch = row
    result = pd.read_csv("family_list.csv")

    for row in result :

        if tomatch == "HIGH-CPU, MID-GPU, HIGH-RAM":
            fam_list = "Family 1"
        elif tomatch == "HIGH-CPU, MID-GPU, MID-RAM":
            fam_list = "Family 2"           
        elif tomatch == "HIGH-CPU, MID-GPU, LOW-RAM":
            fam_list = "Family 3"         
        elif tomatch == "HIGH-CPU, HIGH-GPU, HIGH-RAM":
            fam_list = "Family 4"            
        elif tomatch == "HIGH-CPU, HIGH-GPU, MID-RAM":
            fam_list = "Family 5"
        elif tomatch == "HIGH-CPU, HIGH-GPU, LOW-RAM":
            fam_list = "Family 6"
        elif tomatch == "HIGH-CPU, LOW-GPU, HIGH-RAM":
            fam_list = "Family 7"
        elif tomatch == "HIGH-CPU, LOW-GPU, MID-RAM":
            fam_list = "Family 8"
        elif tomatch == "HIGH-CPU, LOW-GPU, LOW-RAM":
            fam_list = "Family 9"
        elif tomatch == "MID-CPU, MID-GPU, HIGH-RAM":
            fam_list = "Family 10"
        elif tomatch == "MID-CPU, MID-GPU, MID-RAM":
            fam_list = "Family 11"
        elif tomatch == "MID-CPU, MID-GPU, LOW-RAM":
            fam_list = "Family 12"
        elif tomatch == "MID-CPU, HIGH-GPU, HIGH-RAM":
            fam_list = "Family 13"
        elif tomatch == "MID-CPU, HIGH-GPU, MID-RAM":
            fam_list = "Family 14"
        elif tomatch == "MID-CPU, HIGH-GPU, LOW-RAM":
            fam_list = "Family 15"
        elif tomatch == "MID-CPU, LOW-GPU, HIGH-RAM":
            fam_list = "Family 16"
        elif tomatch == "MID-CPU, LOW-GPU, MID-RAM":
            fam_list = "Family 17"
        elif tomatch == "MID-CPU, LOW-GPU, LOW-RAM":
            fam_list = "Family 18"
        elif tomatch == "LOW-CPU, MID-GPU, HIGH-RAM":
            fam_list = "Family 19"
        elif tomatch == "LOW-CPU, MID-GPU, MID-RAM":
            fam_list = "Family 20"
        elif tomatch == "LOW-CPU, MID-GPU, LOW-RAM":
            fam_list = "Family 21"
        elif tomatch == "LOW-CPU, HIGH-GPU, HIGH-RAM":
            fam_list = "Family 22"
        elif tomatch == "LOW-CPU, HIGH-GPU, MID-RAM":
            fam_list = "Family 23"
        elif tomatch == "LOW-CPU, HIGH-GPU, LOW-RAM":
            fam_list = "Family 24"
        elif tomatch == "LOW-CPU, LOW-GPU, HIGH-RAM":
            fam_list = "Family 25"
        elif tomatch == "LOW-CPU, LOW-GPU, MID-RAM":
            fam_list = "Family 26"
        elif tomatch == "LOW-CPU, LOW-GPU, LOW-RAM":
            fam_list = "Family 27" 
        else:
            fam_list = np.nan
    
    return fam_list


df['family_class'] = df['merged_cells'].apply(match_list)

df = df.drop(columns=['merged_cells'])

df.family_class.value_counts()
#################### OUPUT THE NEW FILE

writer = pd.ExcelWriter('compiled_pl_26_may_2018.xlsx')
df.to_excel(writer,'total')
writer.save()


 
            
