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
xl = pd.ExcelFile("original_pl.xls")
df = xl.parse("overall")


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
low_gpu_list = ['ARM Mali 450 (750Mhz)','ARM Mali 450 (700Mhz)','ARM Mali 450 (600Mhz)','ARM Mali 450 (533Mhz)','ARM Mali 400 (614Mhz)','ARM Mali 400 (600Mhz)','ARM Mali 400 (533Mhz)','ARM Mali 400 (525Mhz)','ARM Mali 400 (512Mhz)','ARM Mali 400 (500Mhz)','ARM Mali 400 (480Mhz)','ARM Mali 400 (400Mhz)','ARM Mali 400 (384Mhz)','ARM Mali 400 (312Mhz)','ARM Mali 400 (256Mhz)','ARM Mali 400 (250Mhz)','Vivante','Vivante GC 800 (575Mhz)','Vivante GC 4000 (240Mhz)','Qualcomm Adreno 308 (650Mhz)','Qualcomm Adreno 308 (400Mhz)','Qualcomm Adreno 306 (400Mhz)','Qualcomm Adreno 305 (400Mhz)','Qualcomm Adreno 304 (400Mhz)','Qualcomm Adreno 302 (400Mhz)','Qualcomm Adreno 225 (400Mhz)','Qualcomm Adreno 220 (266Mhz)','Qualcomm Adreno 205 (245Mhz)','Qualcomm Adreno 203 (300Mhz)','Qualcomm Adreno 200 (245Mhz)','Qualcomm Adreno 200 (133Mhz)','Imagination Tech PowerVR G6110 (600Mhz)','Imagination Tech PowerVR G6110 (576Mhz)','Imagination Tech PowerVR SGX544 (480Mhz)','Imagination Tech PowerVR SGX544 (357Mhz)','Imagination Tech PowerVR SGX544 (286Mhz)','Imagination Tech PowerVR SGX544 (256Mhz)','Imagination Tech PowerVR SGX544 (156Mhz)','Imagination Tech PowerVR SGX540 (600Mhz)','Imagination Tech PowerVR SGX540 (200Mhz)','Imagination Tech PowerVR SGX531 Ultra (525Mhz)','Imagination Tech PowerVR SGX531 Ultra (522Mhz)','Imagination Tech PowerVR SGX531 (522Mhz)','Imagination Tech PowerVR SGX531 (281Mhz)']
mid_gpu_list = ['Qualcomm Adreno 405 (550Mhz)','Qualcomm Adreno 330 (574Mhz)','Qualcomm Adreno 330 (450Mhz)','Qualcomm Adreno 320 (400Mhz)','ARM Mali T720 (700Mhz)','ARM Mali T720 (675Mhz)','ARM Mali T720 (668Mhz)','ARM Mali T720 (600Mhz)','ARM Mali T720 (550Mhz)','ARM Mali T720 (520Mhz)','ARM Mali T720 (500Mhz)','ARM Mali T720 (450Mhz)','ARM Mali T628 (600Mhz)','ARM Mali T628 (533Mhz)','ARM Mali T624 (600Mhz)','ARM Mali T604 (533Mhz)','ARM Mali T860 (700Mhz)','ARM Mali T860 (650Mhz)','ARM Mali T860 (600Mhz)','ARM Mali T860 (550Mhz)','ARM Mali T860 (520Mhz)','ARM Mali T860 (350Mhz)','ARM Mali T830 (950Mhz)','ARM Mali T830 (900Mhz)','ARM Mali T830 (700Mhz)','ARM Mali T820 (750Mhz)','ARM Mali T820 (650Mhz)']
high_gpu_list = ['Qualcomm Adreno 630','Qualcomm Adreno 540 (650Mhz)','Qualcomm Adreno 530 (653Mhz)','Qualcomm Adreno 512 (650Mhz)','Qualcomm Adreno 510 (600Mhz)','Qualcomm Adreno 508 (650Mhz)','Qualcomm Adreno 506 (650Mhz)','Qualcomm Adreno 506 (600Mhz)','Qualcomm Adreno 505 (450Mhz)','Qualcomm Adreno 430 (650Mhz)','Qualcomm Adreno 420 (600Mhz)','Qualcomm Adreno 418 (600Mhz)','Imagination Tech PowerVR GT7400 Plus (800Mhz)','Imagination Tech PowerVR GX6250 (600Mhz)','Imagination Tech PowerVR GE8300 (500Mhz)','Imagination Tech PowerVR GE8300 (400Mhz)','Imagination Tech PowerVR GE8100 (570Mhz)','Imagination Tech PowerVR GE8100 (450Mhz)','Imagination Tech PowerVR G6200 (700Mhz)','Imagination Tech PowerVR G6200 (600Mhz)','ARM Mali G72 (900Mhz)','ARM Mali G71 (550Mhz)','ARM Mali G71 (1300Mhz)','ARM Mali G71 (1037Mhz)','ARM Mali T880 (900Mhz)','ARM Mali T880 (850Mhz)','ARM Mali T880 (780Mhz)','ARM Mali T880 (650Mhz)','ARM Mali T880 (1000Mhz)','ARM Mali T760 (772Mhz)','ARM Mali T760 (700Mhz)','ARM Mali T760 (600Mhz)','ARM Mali T760 (500Mhz)','ARM Mali T750 (500Mhz)']
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
    
df['GPU_FAM'] = df['GPU'].apply(add_gpu_fam)

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

gpu_filling = 'MID-GPU'
df['GPU_FAM'] = df.apply(lambda row: "MID-GPU")
df['GPU_FAM'].isnull().sum()


#################### OUPUT THE NEW FILE

writer = pd.ExcelWriter('compiled_pl.xlsx')
df.to_excel(writer,'total')
writer.save()


 
            
