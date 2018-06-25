#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 09:46:02 2018

@author: macintosh
"""

import pandas as pd
import numpy as np
from collections import Counter

#Get both files: The last PL + the Roseta file.
xl = pd.ExcelFile("cosmin_pl.xls")
df = xl.parse("Report")
xl_ros = pd.ExcelFile("rosetta.xlsx")
roseta_df = xl_ros.parse("total")

gppa_xl = pd.ExcelFile("gppa.xlsx")
gppa = gppa_xl.parse("GPPA")


#Convert columns to string for concatenations
roseta_df['Retail Branding (A)'] =  roseta_df['Retail Branding (A)'].astype(str)
roseta_df['Marketing Name (D)'] = roseta_df['Marketing Name (D)'].astype(str)
roseta_df['TKDB Name (G)'] = roseta_df['TKDB Name (G)'].astype(str)
#Concatenate Retail + Marketing name
roseta_df['brand_marketing'] = roseta_df['Retail Branding (A)'] + " " + roseta_df['Marketing Name (D)']


#When the DEVICE CODE repeats and the brand_marketing also repeats I want to concatenate all the TKDB names in one
roseta_lite = pd.DataFrame()
roseta_lite_nobrand = pd.DataFrame()
roseta_lite = roseta_df.groupby(['Device (C)', 'brand_marketing'])['TKDB Name (G)'].apply('___'.join).reset_index()
roseta_lite_nobrand = roseta_df.groupby(['Device (C)'])['TKDB Name (G)'].apply('___'.join).reset_index()


roseta_lite_nobrand.loc[roseta_lite_nobrand['Device (C)'] == 'gta2slte']


#Create a merged DF between the NEW_DF and rteh
pl_roseta_lite_merged = pd.merge(df, roseta_lite,  how='left', left_on=['device code', 'name'], right_on = ['Device (C)', 'brand_marketing'])
pl_roseta_lite_merged.drop(columns=['Device (C)', 'brand_marketing'], inplace=True)

#To make sure all Nans are really nans
pl_roseta_lite_merged.replace("-",np.nan, inplace=True)
pl_roseta_lite_merged.replace("nan",np.nan, inplace=True)

#Split by Not NAN and NAN to later concat
pl_roseta_lite_merged_withNAN = pl_roseta_lite_merged[pl_roseta_lite_merged['TKDB Name (G)'].isnull()]
pl_roseta_lite_merged_withoutNAN = pl_roseta_lite_merged[pl_roseta_lite_merged['TKDB Name (G)'].notnull()]
pl_roseta_lite_merged_withNAN = pd.merge(pl_roseta_lite_merged_withNAN, roseta_lite_nobrand,  how='left', left_on=['device code'], right_on = ['Device (C)'])
pl_roseta_lite_merged_withNAN.drop(columns=['Device (C)', 'TKDB Name (G)_x'], inplace=True)
pl_roseta_lite_merged_withNAN.rename(columns={'TKDB Name (G)_y': 'TKDB Name (G)'}, inplace=True)
df = pd.concat([pl_roseta_lite_merged_withNAN,pl_roseta_lite_merged_withoutNAN ])

#Get device count
def identified_devices(row):
    if str(row) != 'nan' or str(row) != np.nan:
        return len(str(row).split('___'))

df['identified'] = df['TKDB Name (G)'].apply(identified_devices)
             
def device_by_location(row):
    split_row = str(row).split("___")
    indexes_list=[]
    location_list = []
    if len(split_row) > 1:
        location_list = []
        for x in range(0,len(split_row)):
            indexes = (gppa['Device'].loc[gppa['Device'] == split_row[x]].index)
            for y in range(0,len(indexes)):
                if indexes[y] not in indexes_list:
                    indexes_list.append(indexes[y])
        for x in range(len(indexes_list)):
            location = str(gppa['Location'].iloc[indexes_list[x]])
            location_list.append(location)
        c = Counter(location_list)
        concatenate_all = str(c['DaNang']) + "/" + str(c['Hanoi']) + "/"  + str(c["Saigon 2"]) + "/" + str(c["Mexico"]) + "/" + str(c["Yogyakarta 1"]) + "/" + str(c["Yogyakarta 2"])
        return concatenate_all
    #[X]If it's just one device in the ROW
    elif len(split_row) <= 1:
        indexes = gppa['Device'].loc[gppa['Device'] == split_row[0]].index
        location_list = []
        for x in range(0,len(indexes)):
            location = str(gppa['Location'].iloc[indexes[x]])
            location_list.append(location)
        c = Counter(location_list)
        concatenate_all = str(c['DaNang']) + "/" + str(c['Hanoi']) + "/"  + str(c["Saigon 2"]) + "/" + str(c["Mexico"]) + "/" + str(c["Yogyakarta 1"]) + "/" + str(c["Yogyakarta 2"])
        return concatenate_all

device_by_location('ZTE BLADE A601___ZTE BLADE A601')
    
df['All']  = df['TKDB Name (G)'].apply(device_by_location)


df['All'].replace(np.nan, '0/0/0/0/0/0', inplace=True)
df['DAD'], df['HAN'],df['SA2'], df['MEX'],df['JOG1'],df['JOG2']  = df['All'].str.split('/', 6).str
df.drop(columns=['All', 'Unnamed: 26'], inplace=True)

writer = pd.ExcelWriter('cosmin_pl_25june_fixed_ultimate.xlsx')
df.to_excel(writer,'total')
writer.save()

