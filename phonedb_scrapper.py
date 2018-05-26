#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 24 12:45:13 2018

@author: ruben.ramirez
"""

##Imports
import pandas as pd
from bs4 import BeautifulSoup
import requests as r

##Base link to connect to PhoneDB
baseURL = 'http://phonedb.net/'



##Get all pages links###################################################################
links_df = pd.DataFrame()
base_devices_detail_url = 'http://phonedb.net/index.php?m=device&s=list&filter='

for i in range(228):
    global links_df
    page = i * 59
    url = base_devices_detail_url + str(page)
    links_df = links_df.append(pd.DataFrame({'full_link': url}, index = [0]),ignore_index=True)
##########################################################################################

##CREATE AN EMPTY LINK DF DATA FRAME
df = pd.DataFrame()
for link in links_df['full_link']:
    source_code=r.get(link)
    plain_text=source_code.text
    soup = BeautifulSoup(plain_text)
    soup_data = soup.find_all('div', class_='content_block')
    ##FOR EACH LINK, STORE IT IN THE DF
    for each in soup_data:
        if len(each.find_all('a')) > 0:
            detail_link = each.find_all('a')[0]['href']
            full_url =  baseURL+detail_link
            df = df.append(pd.DataFrame({'full_link': full_url}, index = [0]),ignore_index=True)


##Phone Details ########
device_specs = pd.DataFrame()

#for link in df['full_link']:
for link in df.full_link[1059:2000]:
    phone_source_code=r.get(link)
    phone_plain_text=phone_source_code.text
    phone_soup = BeautifulSoup(phone_plain_text, 'lxml')
    table = phone_soup.find('table')
    if table.find('a', id='datasheet_item_id2') is not None:
        name = table.find('a', id='datasheet_item_id2').parent.text #Title
    if table.find('a', id='datasheet_item_id49') is not None:
        ram = table.find('a', id='datasheet_item_id49').parent.text.split(' ')[0] #Ram
    if table.find('a', id='datasheet_item_id147') is not None:    
        gpu = table.find('a', id='datasheet_item_id147').parent.text #GPU
    if table.find('a', id='datasheet_item_id36') is not None: 
        cpu = table.find('a', id='datasheet_item_id36').parent.text #CPU
    device_specs = device_specs.append(pd.DataFrame({'model': name, 'ram': ram, 'gpu': gpu, 'cpu': cpu}, index = [0]),ignore_index=True)
    print("finish row" + " " + str(link))



