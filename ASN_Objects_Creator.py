#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:08:22 2020

@author: jacksonbrietzke
@author: rajatsingh
"""

import pandas as pd
import numpy as np
import re
import csv
import argparse
import redis
import pickle

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

    def __init__(self, as_number):
        try:
            self.as_number = int(float(as_number))
        except Exception as e:
            print(e)
            self.as_number = 'Undefined'
        self.events_list = []
        self.score = 0

    def create_score(self):
        for x in self.events_list:
            try:
                self.score += x.score
            except Exception as e:
                print(e)


def print_asn_obj(asn_obj):
    pass

def main():

    r = redis.Redis(host='localhost', port=6379, db=0)
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--infile', dest='infile', help='csv file path')
    parser.add_argument('--outfile', dest='outfile', help='output ASN/Score file path')

    args = parser.parse_args()

    print("Creating ASN Objects")
    asn_objects = []
    for x in range(0,500000):
        asn_objects.append(ASN(x))

    master_df = pd.read_csv(args.infile, low_memory=False)
    master_df.sort_values(by='ASN', inplace=True)
    for x in range(len(master_df.index)):
        temp_event = Event(master_df['ID'][x], master_df['IP_Address'][x],
                           master_df['Confidence'][x], master_df['Hostility'][x],
                           master_df['Reputation_Rating'][x])
        asn_objects[master_df['ASN'][x]].events_list.append(temp_event)

    pickled_asn_objs = pickle.dumps(asn_objects)
    r.set('asn_objects', pickled_asn_objs)

    #prints long ass string
    #print(r.get('asn_objects'))


    with open(args.outfile, 'w') as file:

       writer = csv.writer(file)
       writer.writerow(['ASN', 'Score'])
       for x in asn_objects:
           x.create_score()
           writer.writerow([x.as_number, x.score])



if __name__ == "__main__":
    main()
