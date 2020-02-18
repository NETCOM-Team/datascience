#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 19:16:08 2020

@author: jacksonbrietzke
"""

import pandas as pd
def main():
    print("Appending to cleaned")
    cleaned_badness_output_file = '../Data/Output/MASTER_Badness.csv'
    master_df = pd.read_csv('../Data/Output/MASTER.csv')
    asn_score_df = pd.read_csv('../Data/Output/ASN_Scores.csv')
    badness_list = []
    event_score_list = []

    for index, row in master_df.iterrows():
        badness_list.append(asn_score_df['Badness'][row['ASN']])
#        print(type(row['Hostility']))
        if(row['Hostility'] > 0):
            event_score = (row['Confidence'] + 
                           row['Hostility'] + 
                           row['Reputation_Rating']) / 20
        else:
            event_score = (row['Confidence'] + 
                           row['Reputation_Rating']) / 15
        
        event_score_list.append(event_score)
    master_df['Event_Score'] = event_score_list    
    master_df['ASN_Badness'] = badness_list
    master_df.to_csv(cleaned_badness_output_file)
    
main()