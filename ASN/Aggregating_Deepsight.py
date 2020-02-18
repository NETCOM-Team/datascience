#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import os
import ipaddress
import pickle
#from netaddr import CIDR, IP
#Creating CSVs from Deepsight Data
def creating_files(inputPath, outputPath):
    print("Creating Files")
#    inputPath = 'Data/'
#    outputPath = 'Data/Output/'
    master_output = '/MASTER.csv'
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
    ipMaster_df = create_ip_url_master_df(inputPath, outputPath, ipFiles, c_size, ip_data_fields, "/IP_Master")     
    urlMaster_df = create_ip_url_master_df(inputPath, outputPath, urlFiles, c_size, url_data_fields, "/URL_Master")
    ipMaster_df.rename(columns=ipNamesDict, inplace=True)
    urlMaster_df.rename(columns=urlNamesDict, inplace=True)
    total_master = pd.concat([ipMaster_df,urlMaster_df], axis=0, ignore_index=True, sort=False)
    total_master = dropping_multiple_ips_asns(inputPath, total_master)
    total_master.to_csv(outputPath + master_output)

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
#        df_chunk.to_csv(outputPath + 'output_' + file)
    
#    df.to_csv(outputPath + 'output_' + outputName + '.csv')
    return df

#Getting rid of multiple IPs and ASNs
def dropping_multiple_ips_asns(inputPath, df):
    print("Dropping multiple IPs and ASNs")
#    geoPath = inputPath + '/geolite3.csv'
#    geo_df = pd.read_csv(geoPath)
#    with open(inputPath + '/cached_list.txt', "rb") as fp:   # Unpickling
#        cached_list = pickle.load(fp)
#    cached_list = creating_cached_list(geo_df, inputPath)
#    print(cached_list)
#    for x in cached_list:
#        for y in x:
#            print(y)
#    exit()
    drop_set = set()
    print('Looping through dataframe')
    for x in range(len(df.index)):
        if(str(df['IP_Address'][x]) == 'nan'):
            drop_set.add(x)
        elif(len(str(df['IP_Address'][x])) > 15):
#            cleaning_multiple_ips(df['IP_Address'][x], geo_df, cached_list)
            drop_set.add(x)
        elif(str(df['ASN'][x]) == 'nan'):
            drop_set.add(x)
        elif(len(str(df['ASN'][x])) > 12):
            drop_set.add(x)
    
    df.drop(drop_set, inplace = True)
    df['ASN'] = pd.to_numeric(df['ASN'], downcast='integer')
    df.sort_values(by=['ASN','Source_Date'], inplace=True)
    return df

def cleaning_multiple_ips(ips, geo_df, cached_list):
    print('Cleaning Multiple Ips')
    ips = ips.split(',')
    for x in range(len(ips)):
        asn = find_ip_asn(ips[x], geo_df, cached_list)
        print('This is the ASN: ', asn)
        ips[x] = [ips[x], asn]
    print(ips)
    return ips
        
def find_ip_asn(ip, geo_df, cached_list):
    print('Find IP ASN')
    temp = ip.split('.')
    for x in range(0,4):
            temp[x] = int(temp[x])
    print('This is x: ', temp[0], type(temp[0]))
    print('This is IP: ', ip)
    try:
        start = cached_list[temp[0]-1][temp[1]-1]
        end = cached_list[temp[0]][temp[1]]
    except:
        print('Error This is x: ', x)
        return
    
    print('Start and End', start,end)
    
#    exit()
    for x in range(start, end):
        print("In Start End loop")
#        for index, row in geo_df.iterrows():
        print(geo_df['IP_CIDR'][x])
        print(ipaddress.ip_address(ip))
        if(ipaddress.ip_address(ip) in ipaddress.ip_network(geo_df['IP_CIDR'][x])):
            print("THIS IS HIT\n\n\n")
            exit()
            return geo_df['ASN'][x]
    return -1        

def creating_cached_list(geo_df, inputPath):
    print("Creating Cached List")
    cl0 = [0] * 256
    cl1 = [0] * 256
    cl2 = [0] * 256
    current_ip = [0,0,0]
    for index, row in geo_df.iterrows():
        temp = row['IP_List'].strip('][').split(', ')
        for x in range(0,4):
            temp[x] = int(temp[x])
#        print("row['IP_List']", row['IP_List'], type(row['IP_List']))
#        print(temp, type(temp))
#        print(current_ip[0], current_ip[1], current_ip[2])
        if(current_ip[0] != temp[0]):
            cl0[current_ip[0]] = cl1
            current_ip[0] = temp[0]
            cl1[current_ip[1]] = index
            current_ip[1] = temp[1]
        elif(current_ip[1] != temp[1]):
            cl1[current_ip[1]] = index
            current_ip[1] = temp[1]
           
            
    cached_list = cl0
    with open(inputPath + '/cached_list.txt', "wb") as fp:   #Pickling
        pickle.dump(cached_list, fp)
    return cached_list
        