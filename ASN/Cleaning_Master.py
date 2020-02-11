#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 09:08:30 2020

@author: jacksonbrietzke
"""

import pandas as pd

#Cleaning master csv to only 1 IP and 1 ASN
def cleaning_master():
    print("Cleaning Master")
    master_df = pd.read_csv('Data/Output/MASTER.csv', low_memory=False)
    drop_set = set()
    for x in range(len(master_df.index)):
        if(str(master_df['IP_Address'][x]) == 'nan'):
            drop_set.add(x)
        elif(len(str(master_df['IP_Address'][x])) > 15):
            drop_set.add(x)
        elif(str(master_df['ASN'][x]) == 'nan'):
            drop_set.add(x)
        elif(len(str(master_df['ASN'][x])) > 12):
            drop_set.add(x)
    
    master_df.drop(drop_set, inplace = True)
    master_df.drop(master_df.columns[0], axis = 1, inplace = True)
    master_df['ASN'] = pd.to_numeric(master_df['ASN'], downcast='integer')
    master_df.sort_values(by='ASN', inplace=True)
    master_df.to_csv('Data/Output/CLEANED.csv')
    
