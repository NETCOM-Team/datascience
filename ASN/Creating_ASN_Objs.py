#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:08:22 2020

@author: jacksonbrietzke
@author: rajsingh
"""

import pandas as pd
import csv
from operator import itemgetter
import networkx as nx
from networkx.algorithms import community
import ast
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
        self.has_events = False
        self.ev_centrality = 0
        self.katz_centrality = 0

    def __init__(self, as_number):
        try:
            self.as_number = int(float(as_number))
        except Exception as e:
            print(e)
            self.as_number = 'Undefined'
        self.events_list = []
        self.score = 0
        self.total_ips = 0
        self.badness = 0
        self.has_events = False
        self.ev_centrality = 0
        self.katz_centrality = 0

    def create_score(self):
        for x in self.events_list:
            try:
                self.score += x.score
            except Exception as e:
                print(e)

    def set_total_ips (self):
        if(self.total_ips == 0):
            self.total_ips = 256

    def create_badness(self):
        self.badness = self.score / self.total_ips

    def set_ev_centrality(self, ev_centrality):
        self.ev_centrality = ev_centrality

    def set_katz_centrality(self, katz_centrality):
        self.ev_centrality = katz_centrality


def create_asn_graph(asn_obj_dict):
     G = nx.Graph()
     for obj in asn_obj_dict:
         G.add_node(obj.as_number)
         for event in obj.events_list:
             G.add_node(event.ip_address)
             G.add_edge(event.ip_address, obj.as_number)
     return G

def get_eigenvector_centrality(centrality_struct):
     ints = []
     strs = []
     for tup in centrality_struct.items():
         if isinstance(tup[0], int):
             ints.append(tup)
     return ints

def get_katz_centrality(centrality_struct):
     ints = []
     strs = []
     for tup in centrality_struct.items():
         if isinstance(tup[0], int):
             ints.append(tup)
     return ints

# Creating ASN objects for all possible ASNS
def creating_asns(outputPath):

    asn_scores_output = outputPath + '/ASN_Scores.csv'
    geolite_input = outputPath + '/geolite_lookup.csv'
    master_input = outputPath + '/MASTER.csv'
    print("Creating ASN Objects")
    asn_objects = []
    event_objects = []
    MAX_RANGE = 600000
    for x in range(0,MAX_RANGE):
        asn_objects.append(ASN(x))
    geolite_df = pd.read_csv(geolite_input)
    master_df = pd.read_csv(master_input, low_memory=False)
    master_df.sort_values(by='ASN', inplace=True)
    for x in range(len(master_df.index)):
        temp_event = Event(master_df['ID'][x], master_df['IP_Address'][x],
                           master_df['Confidence'][x], master_df['Hostility'][x],
                           master_df['Reputation_Rating'][x])
        asn_objects[master_df['ASN'][x]].events_list.append(temp_event)
        asn_objects[master_df['ASN'][x]].has_events = True

    for obj in asn_objects:
        if obj.has_events:
            event_objects.append(obj)

    print('getting eigenvector centrality')
    G = create_asn_graph(event_objects)
    ev_centrality = nx.eigenvector_centrality_numpy(G)
    #katz_centrality = nx.katz_centrality_numpy(G)
    asn_ev_centralities = get_eigenvector_centrality(ev_centrality)
    #asn_katz_centralities = get_katz_centrality(katz_centrality)

    i = 0
    for obj in event_objects:
        obj.set_ev_centrality(asn_ev_centralities[i])
        #obj.set_katz_centrality(asn_katz_centralities[i])
        i += 1

    #print(asn_objects[0].as_number, asn_objects[0].ev_centrality)

    with open(asn_scores_output, 'w') as file:

       writer = csv.writer(file)
       writer.writerow(['ASN', 'Score', 'Total_IPs', 'Badness', 'Exists', 'EV Centrality'])
       for x in asn_objects:
           x.create_score()
           x.total_ips = geolite_df['Total_IPs'][x.as_number]
#           print(x.max_ips)
           if(x.total_ips > 0 or x.score > 0):
               x.set_total_ips()
               x.create_badness()
               writer.writerow([x.as_number, x.score, x.total_ips, x.badness, True, x.ev_centrality])
           else:
               writer.writerow([x.as_number, x.score, x.total_ips, x.badness, True, x.ev_centrality])
