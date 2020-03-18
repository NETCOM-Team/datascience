#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:08:22 2020

@author: jacksonbrietzke
@author: rajsingh
"""

import json
import csv
# import ast
import os
import redis
import pandas as pd
import networkx as nx
import numpy as np
# from operator import itemgetter
# from networkx.algorithms import community

# Event class for each entry in Datafeed


class Event:
    """Creating Class Events for ASN objects."""
    def __init__(self, event_id, ip_address, confidence,
                 hostility, reputation_rating):
        self.event_id = event_id
        self.ip_address = ip_address
        try:
            self.confidence = int(confidence)
        except ValueError:
            self.confidence = 0
        try:
            self.hostility = int(hostility)
        except ValueError:
            self.hostility = 0
        try:
            self.reputation_rating = int(reputation_rating)
        except ValueError:
            self.reputation_rating = 0
        self.score = self.create_score()

    def create_score(self):
        """Creating Score for Event."""
        temp_score = self.hostility + self.confidence + self.reputation_rating
        if self.hostility == 0:
            temp_score = temp_score / 15
        else:
            temp_score = temp_score / 20
        return temp_score

# ASN object to use for future work


class ASN:
    """Creating ASN Class."""
    def __init__(self, as_number):
        """Initializing Instance."""
        try:
            self.as_number = int(float(as_number))
        except ValueError:
            self.as_number = False
        self.events_list = []
        self.score = 0
        self.total_ips = False
        self.badness = 0
        self.has_events = False
        self.ev_centrality = 0
        self.katz_centrality = 0

    @classmethod
    def given_asn(cls, as_number):
        """Initializing Instance with ASN."""
        return cls(as_number)

    def create_score(self):
        """Creating ASN score."""
        temp_score = 0
        for event in self.events_list:
            temp_score += event.score
        self.score = temp_score

    def set_total_ips(self):
        """Setting total IPs for ASN."""
        if self.total_ips is False or self.total_ips == 0:
            self.total_ips = 256

    def create_badness(self):
        """Creating badness score for ASN."""
        self.badness = self.score / self.total_ips

    def set_ev_centrality(self, ev_centrality):
        """Setting EV Centrality for ASN."""
        self.ev_centrality = ev_centrality

    @staticmethod
    def serialize_asn(asn_obj):
        """Static method for Serializing ASN."""
        serialized_events = []
        for event in asn_obj.events_list:
            serialized_events.append(event.__dict__)
        asn_obj.events_list = json.dumps(serialized_events)
        return json.dumps(asn_obj.__dict__, sort_keys=True, cls=PandasEncoder)


class PandasEncoder(json.JSONEncoder):
    """Custom encoder for Redis."""
    def default(self, obj):
        if isinstance(obj, np.int64):
            obj = int(obj)
        elif isinstance(obj, np.float64):
            obj = float(obj)
        else:
            obj = super(PandasEncoder, self).default(obj)
        return obj


def create_asn_graph(asn_obj_dict):
    """Creating ASN graph."""
    graph = nx.Graph()
    for obj in asn_obj_dict:
        graph.add_node(obj.as_number)
        for event in obj.events_list:
            graph.add_node(event.ip_address)
            graph.add_edge(event.ip_address, obj.as_number)
    return graph


def get_eigenvector_centrality(centrality_struct):
    """Getting the Eigenvector Centraility."""
    ints = []
    for tup in centrality_struct.items():
        if isinstance(tup[0], int):
            ints.append(tup)
    return ints


def create_max_asn_objects():
    """Creating Max ASN Objects"""
    max_range = 600000
    asn_list = []
    for number in range(0, max_range):
        asn_list.append(ASN(number))
    return asn_list


def updating_master_and_scores(master_df, asn_objects,
                               geolite_df, master_input):
    """Updating master and scores."""
    print('Updating Master and Scores')
    asn_chrono_score_list = []
    event_score = []
    for number in range(len(master_df.index)):
        as_number = master_df['ASN'][number]
        temp_event = Event(master_df['ID'][number],
                           master_df['IP_Address'][number],
                           master_df['Confidence'][number],
                           master_df['Hostility'][number],
                           master_df['Reputation_Rating'][number])
        asn_objects[as_number].events_list.append(temp_event)
        event_score.append(temp_event.create_score())
        if asn_objects[as_number].total_ips is False:
            asn = asn_objects[as_number].as_number
            asn_objects[as_number].total_ips = geolite_df['Total_IPs'][asn]
            asn_objects[as_number].set_total_ips()
        asn_objects[as_number].create_score()
        asn_objects[as_number].create_badness()
        asn_chrono_score_list.append(asn_objects[as_number].badness)
#        asn_objects[master_df['ASN'][x]].events_list.append(temp_event)
        asn_objects[as_number].has_events = True
    master_df['Event_Score'] = event_score
    master_df['Historical_Score'] = asn_chrono_score_list
    master_df.to_csv(master_input)
    return asn_objects


def creating_asns(output_path):
    """Creating ASN Objects."""
    print("Creating ASN Objects")
    asn_scores_output = output_path + '/ASN_Scores.csv'
    geolite_input = output_path + '/geolite_lookup.csv'
    master_input = output_path + '/MASTER.csv'
    asn_objects = create_max_asn_objects()
    geolite_df = pd.read_csv(geolite_input)
    master_df = pd.read_csv(master_input, low_memory=False)
    master_df.sort_values(by=['ASN', 'Source_Date'], inplace=True)
    asn_objects = updating_master_and_scores(master_df, asn_objects,
                                             geolite_df, master_input)
    creating_asn_evs(asn_objects)
    outputting_asns(asn_scores_output, asn_objects)


def creating_asn_evs(asn_objects):
    """Creating ASN EVs"""
    print('Getting eigenvector centrality')
    event_objects = []
    for obj in asn_objects:
        if obj.has_events:
            event_objects.append(obj)
    graph = create_asn_graph(event_objects)
    ev_centrality = nx.eigenvector_centrality_numpy(graph)
    asn_ev_centralities = get_eigenvector_centrality(ev_centrality)

    i = 0
    for obj in event_objects:
        obj.set_ev_centrality(asn_ev_centralities[i])
        i += 1


def outputting_asns(output_file, asn_objects):
    """Outputting ASN Scores."""
    redis_host = os.getenv('REDIS_HOST')
    redis_instance = redis.Redis(host=redis_host, port=6379)
    with open(output_file, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['ASN', 'Score', 'Total_IPs',
                         'Badness', 'Exists', 'EV Centrality'])
        for asn in asn_objects:
            redis_instance.set(asn.as_number, ASN.serialize_asn(asn))
            if(asn.total_ips > 0 or asn.score > 0):
                writer.writerow([asn.as_number, asn.score, asn.total_ips,
                                 asn.badness, True, asn.ev_centrality])
            else:
                writer.writerow([asn.as_number, asn.score, asn.total_ips,
                                 asn.badness, False, asn.ev_centrality])
