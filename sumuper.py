#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 12:01:54 2018

@author: macintosh
"""

import pandas as pd
import numpy as np

df = pd.read_excel("compiled_pl_5_6_18_aspectratio.xlsx")
df.head()


pivotDF = pd.pivot_table(df,index=["family_class", "GPU"], 
                         values=['Revenue Share', 'CPU'],aggfunc={"Revenue Share":np.sum,"CPU":len}, margins=True)

pivotTot = pivotDF.groupby(['family_class']).sum()
pivotTot.index = [pivotTot.index, ['Total'] * len(pivotTot)]

pivotDF = pd.concat([pivotDF, pivotTot]).sort_index().append(pivotDF.sum().rename(('Grand', 'Total')))

pivotDF.columns = ['Device Count', 'Sum of Revenue Share']

writer = pd.ExcelWriter('pivotedPL.xlsx')
pivotDF.to_excel(writer,'total')
writer.save()
            