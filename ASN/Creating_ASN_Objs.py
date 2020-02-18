#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:08:22 2020

@author: jacksonbrietzke
"""

import pandas as pd
import csv

#Event class for each entry in Datafeed
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
        temp_score = self.hostility + self.confidence + self.reputation_rating
        try:
            if(self.hostility == 0):
                return (temp_score / 15)
            else:
                return (temp_score / 20)
        except Exception as e:
            print(e)

#ASN object to use for future work
class ASN:
    def __init__(self):
        self.as_number = 'TBD'
        self.events_list = []
        self.score = 0
        self.total_ips = 0
        self.badness = 0

    def __init__(self, as_number):
        try:
            self.as_number = int(float(as_number))
        except Exception as e:
            print(e)
            self.as_number = 'Undefined'
        self.events_list = []
        self.score = 0
        self.total_ips = False
        self.badness = 0

    def create_score(self):
        temp_score = 0
        for x in self.events_list:
            try:
                temp_score += x.score
            except Exception as e:
                print(e)
                
        self.score = temp_score
        
    def set_total_ips (self):
        if(self.total_ips == False):
            self.total_ips = 256

    def create_badness(self):
        self.badness = self.score / self.total_ips


# Creating ASN objects for all possible ASNS
def creating_asns(outputPath):

    asn_scores_output = outputPath + '/ASN_Scores.csv'
    geolite_input = outputPath + '/geolite_lookup.csv'
    master_input = outputPath + '/MASTER.csv'
    print("Creating ASN Objects")
    asn_objects = []
    MAX_RANGE = 600000
    for x in range(0,MAX_RANGE):
        asn_objects.append(ASN(x))
    geolite_df = pd.read_csv(geolite_input)
    master_df = pd.read_csv(master_input, low_memory=False)
    master_df.sort_values(by=['ASN','Source_Date'], inplace=True)
    asn_chrono_score_list = []
    event_score = []
    for x in range(len(master_df.index)):
        as_number = master_df['ASN'][x]
        temp_event = Event(master_df['ID'][x], master_df['IP_Address'][x],
                           master_df['Confidence'][x], master_df['Hostility'][x],
                           master_df['Reputation_Rating'][x])
        asn_objects[as_number].events_list.append(temp_event)
        event_score.append(temp_event.create_score())
        if(asn_objects[as_number].total_ips == False):
            asn_objects[as_number].total_ips = geolite_df['Total_IPs'][asn_objects[as_number].as_number]
            asn_objects[as_number].set_total_ips()
        asn_objects[as_number].create_score()
        asn_objects[as_number].create_badness()
        asn_chrono_score_list.append(asn_objects[as_number].badness)
    master_df['Event_Score'] = event_score
    master_df['Historical_Score'] = asn_chrono_score_list
    
    master_df.to_csv(master_input)
    with open(asn_scores_output, 'w') as file:
       writer = csv.writer(file)
       writer.writerow(['ASN', 'Score', 'Total_IPs', 'Badness', 'Exists'])
       for x in asn_objects:
           if(x.total_ips > 0 or x.score > 0):
               writer.writerow([x.as_number, x.score, x.total_ips, x.badness, True])
           else:
               writer.writerow([x.as_number, x.score, x.total_ips, x.badness, False])
