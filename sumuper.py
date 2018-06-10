#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 12:01:54 2018

@author: macintosh
"""

import pandas as pd
import numpy as np

df = pd.read_excel("pl_9june.xlsx")
df.head()


#Ruben from the future. Do not attempt to modify this. It's risky.
pivotDF = pd.pivot_table(df,index=["family_class", "GPU"], 
                         values=['Revenue Share', 'CPU'],aggfunc={"Revenue Share":np.sum,"CPU":len}, margins=True)
pivotTot = pivotDF.groupby(['family_class']).sum()
pivotTot.index = [pivotTot.index, ['Total'] * len(pivotTot)]
pivotDF = pd.concat([pivotDF, pivotTot]).sort_index().append(pivotDF.sum().rename(('Grand', 'Total')))
pivotDF.columns = ['Device Count', 'Sum of Revenue Share']


#Excel exporter and formater
writer = pd.ExcelWriter('PL_9jun_sumup.xlsx', engine='xlsxwriter')
pivotDF.to_excel(writer,'total')
workbook  = writer.book
worksheet = writer.sheets['total']
percentageFormat = workbook.add_format({'num_format': '0.0000%'})
worksheet.set_column('D:D', None, percentageFormat)
writer.save()
            