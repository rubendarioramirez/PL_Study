#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 09:46:02 2018

@author: macintosh
"""

import pandas as pd
import numpy as np

#Get both files: The last PL + the Roseta file.
xl = pd.ExcelFile("pl_ultimate_updated.xlsx")
df = xl.parse("total")
xl_ros = pd.ExcelFile("rosetta.xls")
roseta_df = xl_ros.parse("total")


#Convert columns to string for concatenations
roseta_df['Retail Branding (A)'] =  roseta_df['Retail Branding (A)'].astype(str)
roseta_df['Marketing Name (D)'] = roseta_df['Marketing Name (D)'].astype(str)
roseta_df['TKDB Name (G)'] = roseta_df['TKDB Name (G)'].astype(str)
#Concatenate Retail + Marketing name
roseta_df['brand_marketing'] = roseta_df['Retail Branding (A)'] + " " + roseta_df['Marketing Name (D)']

#roseta_df[roseta_df.loc[:, 'Device (C)'] == 'j7y17lte']

#When the DEVICE CODE repeats and the brand_marketing also repeats I want to concatenate all the TKDB names in one
roseta_lite = pd.DataFrame()
roseta_lite_nobrand = pd.DataFrame()
roseta_lite = roseta_df.groupby(['Device (C)', 'brand_marketing'])['TKDB Name (G)'].apply('___'.join).reset_index()
roseta_lite_nobrand = roseta_df.groupby(['Device (C)'])['TKDB Name (G)'].apply('___'.join).reset_index()


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


writer = pd.ExcelWriter('pl_tkdb_19june.xlsx')
df.to_excel(writer,'total')
writer.save()

