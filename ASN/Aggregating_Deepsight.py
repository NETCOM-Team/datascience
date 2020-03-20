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
import sys
# from netaddr import CIDR, IP
# Creating CSVs from Deepsight Data


def creating_files(input_path, output_path):
    """Creating Files."""
    print("Creating Files")
    master_output = '/MASTER.csv'
    ipFileNames = "Deepsight IP"
    urlFileNames = "Deepsight URL"
    ipFiles = []
    urlFiles = []

    c_size = 1000
    with open(input_path + 'ip_data_fields.txt') as f:
        ip_data_fields = f.read().splitlines()
    with open(input_path + 'url_data_fields.txt') as f:
        url_data_fields = f.read().splitlines()
#    sys.exit()
#    ip_data_fields = ['Id', 'Data Type', 'feed.feed_source_date',
#                      'ip.address', 'ip.asn', 'ip.confidence',
#                      'ip.connection.carrier',
#                      'ip.connection.second_level_domain',
#                      'ip.connection.top_level_domain',
#                      'ip.consecutiveListings', 'ip.hostility',
#                      'ip.location.country_code', 'ip.location.latitude',
#                      'ip.location.longitude',
#                      'ip.organization.naics', 'ip.reputationRating']
#    url_data_fields = Id Data Type feed.feed_source_date
#                       xml.domain.ipAddresses.ip.address
#                       xml.domain.ipAddresses.ip.asn
#                       xml.domain.confidence
#                       xml.domain.ipAddresses.ip.connection.carrier
#                       xml.domain.ipAddresses.ip.connection.second_level_domain
#                       xml.domain.ipAddresses.ip.connection.top_level_domain
#                       xml.domain.consecutiveListings
#                       xml.domain.ipAddresses.ip.location.country_code
#                       xml.domain.ipAddresses.ip.location.latitude
#                       xml.domain.ipAddresses.ip.location.longitude
#                       xml.domain.ipAddresses.ip.organization.naics
#                       xml.domain.reputationRating
    ipNamesDict = {'Id': 'ID','Data Type': 'Data_Type',
                   'feed.feed_source_date': 'Source_Date',
                   'ip.address': 'IP_Address','ip.asn': 'ASN',
                   'ip.confidence': 'Confidence',
                   'ip.connection.carrier': 'Connection_Carrier',
                   'ip.connection.second_level_domain': 'Connection_Second_Level_Domain',
                   'ip.connection.top_level_domain': 'Connection_Top_Level_Domain',
                   'ip.consecutiveListings': 'Consecutive_Listings',
                   'ip.hostility': 'Hostility',
                   'ip.location.country_code': 'Country_Code',
                   'ip.location.latitude': 'Latitude',
                   'ip.location.longitude': 'Longitude',
                   'ip.organization.naics': 'Naics',
                   'ip.reputationRating': 'Reputation_Rating'}
    urlNamesDict = {'Id': 'ID',	'Data Type': 'Data_Type',
                    'feed.feed_source_date': 'Source_Date',
                       'xml.domain.ipAddresses.ip.address': 'IP_Address',
                       'xml.domain.ipAddresses.ip.asn': 'ASN',
                       'xml.domain.confidence': 'Confidence',
                       'xml.domain.ipAddresses.ip.connection.carrier': 'Connection_Carrier',
                       'xml.domain.ipAddresses.ip.connection.second_level_domain': 'Connection_Second_Level_Domain',
                       'xml.domain.ipAddresses.ip.connection.top_level_domain': 'Connection_Top_Level_Domain',
                       'xml.domain.consecutiveListings': 'Consecutive_Listings',
                       'xml.domain.ipAddresses.ip.location.country_code': 'Country_Code',
                       'xml.domain.ipAddresses.ip.location.latitude': 'Latitude',
                       'xml.domain.ipAddresses.ip.location.longitude': 'Longitude',
                       'xml.domain.ipAddresses.ip.organization.naics': 'Naics',
                       'xml.domain.reputationRating': 'Reputation_Rating'}
    ipFiles = get_files(input_path, ipFileNames)
    urlFiles = get_files(input_path, urlFileNames)
    ipMaster_df = create_ip_url_master_df(input_path, output_path,
                                          ipFiles, c_size,
                                          ip_data_fields, "/IP_Master")
    urlMaster_df = create_ip_url_master_df(input_path, output_path, urlFiles,
                                           c_size, url_data_fields,
                                           "/URL_Master")
    ipMaster_df.rename(columns=ipNamesDict, inplace=True)
    urlMaster_df.rename(columns=urlNamesDict, inplace=True)
    total_master = pd.concat([ipMaster_df, urlMaster_df], axis=0,
                             ignore_index=True, sort=False)
    total_master = dropping_multiple_ips_asns(input_path, total_master)
    total_master.to_csv(output_path + master_output)


def get_files(input_path, fileNames):
    """Getting Files from directory using convention"""
    file_list = []
    for i in os.listdir(input_path):
        if(i.startswith(fileNames)):
            file_list.append(i)
            print("Creating " + i)
    return file_list


def create_ip_url_master_df(input_path, output_path, files,
                            c_size, data_fields, outputName):
    """Creating DFs for both IP and URL Deepsight Data"""
    df = pd.DataFrame()
    for file in files:
        df_chunk = pd.DataFrame()
        for chunk in pd.read_csv(input_path + '/' + file, chunksize=c_size,
                                 usecols=data_fields):
            df_chunk = pd.concat([df_chunk, chunk])

        df = pd.concat([df, df_chunk])
#        df_chunk.to_csv(output_path + 'output_' + file)

#    df.to_csv(output_path + 'output_' + outputName + '.csv')
    return df


def dropping_multiple_ips_asns(input_path, df):
    """Getting rid of multiple IPs and ASNs"""
    print("Dropping multiple IPs and ASNs")
#    geoPath = input_path + '/geolite3.csv'
#    geo_df = pd.read_csv(geoPath)
#    with open(input_path + '/cached_list.txt', "rb") as fp:   # Unpickling
#        cached_list = pickle.load(fp)
#    cached_list = creating_cached_list(geo_df, input_path)
#    print(cached_list)
#    for x in cached_list:
#        for y in x:
#            print(y)
#    exit()
    drop_set = set()
#    new_df = pd.DataFrame()
    temp_list = []
    print('Looping through dataframe')
    counter = 0
    print("Length of DF: ", len(df.index))
    for x in range(len(df.index)):
        print(counter)
        counter += 1
        ip_addr = str(df['IP_Address'][x])
        if(str(df['IP_Address'][x]) == 'nan'):
            # print(str(df['IP_Address'][x]))
            drop_set.add(x)
        elif(ip_addr[0].isdigit() is False):
            drop_set.add(x)
        elif(len(ip_addr) > 15):
            #            ip_list = cleaning_multiple_ips(df['IP_Address'][x], geo_df, cached_list)
            #            print("This is the IP LIST: ", ip_list)
            #            print(df.iloc[x])
            #            for y in ip_list:
            #                if(y[1] != -1):
            #                    temp_rows = df.iloc[x].copy()
            #                    temp_rows['IP_Address'] = y[0]
            #                    temp_rows['ASN'] = y[1]
            #                    temp_list.append(temp_rows)
            #                print((temp_rows))
            #            temp_row = df[x]
            drop_set.add(x)
        elif(str(df['ASN'][x]) == 'nan'):
            drop_set.add(x)
        elif(len(str(df['ASN'][x])) > 12):
            drop_set.add(x)

    df.drop(drop_set, inplace=True)
    temp_df = pd.DataFrame(temp_list)
    df = df.append(temp_df)
    df['ASN'] = pd.to_numeric(df['ASN'], downcast='integer')
    df.sort_values(by=['ASN', 'Source_Date'], inplace=True)
    return df


def cleaning_multiple_ips(ips, geo_df, cached_list):
    """Handling multiple IP occurrences"""
    print('Cleaning Multiple Ips')
    ips = ips.split(',')
    for x in range(len(ips)):
        asn = find_ip_asn(ips[x], geo_df, cached_list)
#        print('This is the ASN: ', asn)
        ips[x] = [ips[x], asn]
#    print(ips)
    return ips


def find_ip_asn(ip, geo_df, cached_list):
    """Finding IP's ASN"""
#    print('Find IP ASN')
    temp = ip.split('.')
    for x in range(0, 4):
        temp[x] = int(temp[x])
#    print('This is Temp: ', temp[0], type(temp[0]), temp[1], type(temp[1]))
#    print('This is IP: ', ip)
    try:
        #        print("This is cache0: ", cached_list[temp[0]])
        #        print("This is cache1: ", cached_list[temp[0]][temp[1]])
        start = cached_list[temp[0]][temp[1]-1]
        end = cached_list[temp[0]][temp[1]]
    except Exception as E:
        #        print(E, temp[0], temp[1]-1)
        return -1

#    print('Start and End', start,end)

#    exit()
    for x in range(start, end):
        #        print("In Start End loop")
        ##        for index, row in geo_df.iterrows():
        #        print(geo_df['IP_CIDR'][x])
        #        print(ipaddress.ip_address(ip))
        if(ipaddress.ip_address(ip) in
           ipaddress.ip_network(geo_df['IP_CIDR'][x])):
            #            print("THIS IS HIT\n\n\n")
            #            exit()
            return geo_df['ASN'][x]
    return -1


def creating_cached_list(geo_df, input_path):
    """Creating Cached List"""
    print("Creating Cached List")
    cl0 = [0] * 256
    cl1 = [0] * 256
    current_ip = [0, 0]
    for index, row in geo_df.iterrows():
        temp = row['IP_List'].strip('][').split(', ')
        for x in range(0, 4):
            temp[x] = int(temp[x])
#        print("row['IP_List']", row['IP_List'], type(row['IP_List']))
#        print(temp, type(temp))
#        print(current_ip[0], current_ip[1], current_ip[2])
#        if(current_ip[0] != temp[0]):
#            cl0[current_ip[0]] = cl1
#            current_ip[0] = temp[0]
#        print("What is the index: ", index)
#        print("[current_ip[0]] is: ", current_ip[0])
#        print("[current_ip[1]] is: ", current_ip[1])
#        print("cl0[current_ip[0]] is: ", cl0[current_ip[0]])
#        print("cl1[current_ip[1]] is: ", cl1[current_ip[1]])
#        print("temp[0], temp[1]", temp[0], temp[1])

        if(current_ip[0] != temp[0]):
            #           print(current_ip[0])
            cl1[current_ip[1]] = index
            current_ip[1] = temp[1]
            cl0[current_ip[0]] = cl1
            cl1 = [0] * 256
#            print("Break", cl0[current_ip[0]], "\n\n\n\n")
#            print(cl0)
            current_ip[0] = temp[0]

        if(current_ip[1] != temp[1]):
            cl1[current_ip[1]] = index
#            print("Break", cl1[current_ip[1]], "\n\n\n\n")
            current_ip[1] = temp[1]


#        if(c == 7000):
#            exit()
#        else:
#            c += 1
    last = 0
    for x in cl0:
        try:
            for y in x:
                if(y == 0):
                    y = last
                else:
                    last = y
        except Exception as error:
            print(error)
            pass

    cached_list = cl0
#    print("This is being printed", cached_list)
#    exit()
    with open(input_path + '/cached_list.txt', "wb") as fp:
        pickle.dump(cached_list, fp)
    return cached_list
