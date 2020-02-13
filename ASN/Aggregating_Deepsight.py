#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import os

#Creating CSVs from Deepsight Data
def creating_files():
    print("Creating Files")
    inputPath = 'data/'
    outputPath = 'output_initial/'
    ipFileNames = "Deepsight IP"
    urlFileNames = "Deepsight URL"
    ipFiles = []
    urlFiles = []
    
    c_size = 1000
    ip_data_fields = ['Id','Data Type','feed.feed_description','feed.feed_source_date',	
                   'ip.address','ip.asn','ip.confidence'	,'ip.connection.carrier',
                   'ip.connection.second_level_domain',	'ip.connection.top_level_domain',
                   'ip.consecutiveListings','ip.firstSeen','ip.hostility',
                   'ip.location.country_code','ip.location.latitude','ip.location.longitude',
                   'ip.organization.naics','ip.reputationRating']
    url_data_fields = ['Id',	'Data Type','feed.feed_description',	'feed.feed_source_date',
                       'xml.domain.ipAddresses.ip.address','xml.domain.ipAddresses.ip.asn',	
                       'xml.domain.confidence','xml.domain.ipAddresses.ip.connection.carrier',
                       'xml.domain.ipAddresses.ip.connection.second_level_domain',
                       'xml.domain.ipAddresses.ip.connection.top_level_domain',	
                       'xml.domain.consecutiveListings','xml.domain.firstSeen',
                       'xml.domain.ipAddresses.ip.location.country_code',
                       'xml.domain.ipAddresses.ip.location.latitude',
                       'xml.domain.ipAddresses.ip.location.longitude',	
                       'xml.domain.ipAddresses.ip.organization.naics',	
                       'xml.domain.reputationRating']
    ipNamesDict = {'Id':'ID','Data Type':'Data_Type',
                   'feed.feed_description':'Description',
                   'feed.feed_source_date':'Source_Date',	
                   'ip.address':'IP_Address','ip.asn':'ASN',
                   'ip.confidence':'Confidence',
                   'ip.connection.carrier':'Connection_Carrier',
                   'ip.connection.second_level_domain':'Connection_Second_Level_Domain',
                   'ip.connection.top_level_domain':'Connection_Top_Level_Domain',
                   'ip.consecutiveListings':'Consecutive_Listings',
                   'ip.firstSeen':'First_Seen','ip.hostility':'Hostility',
                   'ip.location.country_code':'Country_Code',
                   'ip.location.latitude':'Latitude',
                   'ip.location.longitude':'Longitude',
                   'ip.organization.naics':'Naics',
                   'ip.reputationRating':'Reputation_Rating'}
    urlNamesDict = {'Id':'ID',	'Data Type':'Data_Type',
                    'feed.feed_description':'Description',
                    'feed.feed_source_date': 'Source_Date',
                       'xml.domain.ipAddresses.ip.address':'IP_Address',
                       'xml.domain.ipAddresses.ip.asn':'ASN',	
                       'xml.domain.confidence':'Confidence',
                       'xml.domain.ipAddresses.ip.connection.carrier':'Connection_Carrier',
                       'xml.domain.ipAddresses.ip.connection.second_level_domain':'Connection_Second_Level_Domain',
                       'xml.domain.ipAddresses.ip.connection.top_level_domain':'Connection_Top_Level_Domain',	
                       'xml.domain.consecutiveListings': 'Consecutive_Listings',
                       'xml.domain.firstSeen':'First_Seen',
                       'xml.domain.ipAddresses.ip.location.country_code':'Country_Code',
                       'xml.domain.ipAddresses.ip.location.latitude':'Latitude',
                       'xml.domain.ipAddresses.ip.location.longitude':'Longitude',	
                       'xml.domain.ipAddresses.ip.organization.naics':'Naics',	
                       'xml.domain.reputationRating':'Reputation_Rating'}
    ipFiles = get_files(inputPath, ipFileNames)
    urlFiles = get_files(inputPath, urlFileNames)
    ipMaster_df = create_ip_url_master_df(inputPath, outputPath, ipFiles, c_size, ip_data_fields, "IP_Master")     
    urlMaster_df = create_ip_url_master_df(inputPath, outputPath, urlFiles, c_size, url_data_fields, "URL_Master")
    ipMaster_df.rename(columns=ipNamesDict, inplace=True)
    urlMaster_df.rename(columns=urlNamesDict, inplace=True)
    total_master = pd.concat([ipMaster_df,urlMaster_df], axis=0, ignore_index=True, sort=False)
    total_master.to_csv(outputPath + 'MASTER.csv')

#Getting the files that match a naming convention
def get_files(inputPath, fileNames):
    file_list = []
    for i in os.listdir(inputPath):
        if(i.startswith(fileNames)):
            file_list.append(i)
            print("Creating " + i)
    return file_list

#Creating DFs for both IP and URL Deepsight Data
def create_ip_url_master_df(inputPath, outputPath, files, c_size, data_fields, outputName):
    df = pd.DataFrame()
    for file in files:
        df_chunk = pd.DataFrame()        
        for chunk in pd.read_csv(inputPath + '/' + file,chunksize=c_size, usecols=data_fields):
            df_chunk = pd.concat([df_chunk, chunk])
        
        df = pd.concat([df, df_chunk])
        df_chunk.to_csv(outputPath + 'output_' + file)
    
    df.to_csv(outputPath + 'output_' + outputName + '.csv')
    return df

