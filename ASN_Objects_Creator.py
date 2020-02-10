#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:08:22 2020

@author: jacksonbrietzke
"""

import pandas as pd
import numpy as np
import re
import csv
import subprocess
import ipaddress

class Event:
    def __init__(self,event_id, ip_address, confidence, hostility, reputation_rating):
        try:
            self.event_id = event_id
            self.ip_address = ip_address
            try:
                self.confidence = int(confidence)
            except:
                self.confidence = 0
            try:
                self.hostility = int(hostility)
            except:
                self.hostility = 0
            try:
                self.reputation_rating = int(reputation_rating)
            except:
                self.reputation_rating = 0
            self.score = self.create_score()
        except Exception as e: 
            print(e)
            print(confidence, hostility, reputation_rating)
        
    def create_score(self):
        try:
            return self.confidence + self.reputation_rating
        except Exception as e: 
            print(e)
    
class ASN:
    def __init__(self):
        self.as_number = 'TBD'
        self.events_list = []
        self.score = 0
        self.max_ips = 0
    
    def __init__(self, as_number):
        try:
            self.as_number = int(float(as_number))
        except Exception as e: 
            print(e)
            self.as_number = 'Undefined'
        self.events_list = []
        self.score = 0
        self.max_ips = 0
    
    def create_score(self):
        for x in self.events_list:
            try:
                self.score += x.score
            except Exception as e: 
                print(e)
    
   
        
        
        
def main():
    print("Creating ASN Objects")
    asn_objects = []
    for x in range(0,600000):
        asn_objects.append(ASN(x))
    geolite_df = pd.read_csv('Full/Output/geolite_lookup.csv')
    master_df = pd.read_csv("Full/Output/CLEANED.csv", low_memory=False)
    master_df.sort_values(by='ASN', inplace=True)
    for x in range(len(master_df.index)):
        temp_event = Event(master_df['ID'][x], master_df['IP_Address'][x],
                           master_df['Confidence'][x], master_df['Hostility'][x],
                           master_df['Reputation_Rating'][x])
        asn_objects[master_df['ASN'][x]].events_list.append(temp_event)

    with open('Full/Output/ASN_Scores.csv', 'w') as file:
      
       writer = csv.writer(file)
       writer.writerow(['ASN', 'Score', 'Max_IPs'])
       for x in asn_objects:
           x.create_score()
           x.max_ips = geolite_df['Total_IPs'][x.as_number]
#           print(x.max_ips)
           if(x.score > 0):
               writer.writerow([x.as_number, x.score, x.max_ips])
        
    
if __name__ == "__main__":
    main()
    
    
#def find_ips(self):
#    try:
#        ips = subprocess.check_output("whois -h whois.radb.net -- '-i origin AS" + str(self.as_number) +
#                            "'| grep -Eo '([0-9.]+){4}/[0-9]+'",
#                            shell=True).decode("utf-8")
#    except Exception as e: 
#            print(e)
#            return False
#    return ips.split('\n')[:-1]
#
#def create_max_ips(self):
#    ips = self.find_ips()
#    if(ips != False):
#        try:
#            for y in ips:
#                try:
#                    self.max_ips += ipaddress.ip_network(y).num_addresses
#                except Exception as e: 
#                    print(e)
#        except Exception as e: 
#                print(e)
#    else:
#        pass
