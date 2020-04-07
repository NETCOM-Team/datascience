    #!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import ipaddress
import ASN
import re
import time
import pandas as pd
# from netaddr import CIDR, IP
# Creating CSVs from Deepsight Data


def creating_files(input_path, output_path):
    """Creating Files."""
    print("Creating Files")
    master_output = '/MASTER.csv'
    redis_instance = ASN.creating_asn_objects.start_redis()
    if redis_instance.exists('master_version'):
        print('inside creating_files;')
        master_version = int(redis_instance.get('master_version').decode('utf-8'))
        print('master version: {}'.format(master_version))
        print('master version type: {}'.format(type(master_version)))
        if master_version > 1:
            print('master version bigger than 1?: {}'.format(master_version))
            master_output = '/MASTER' + str(master_version) + '.csv'
            ASN.creating_asn_objects.stop_redis(redis_instance)
    else:
        ASN.creating_asn_objects.stop_redis(redis_instance)

    file_name = "Deepsight"
    files = []
    names_dict = {}
    c_size = 1000
    with open(input_path + 'data_fields.txt') as file:
        data_fields = file.read().splitlines()
    with open(input_path + 'names_dict.txt') as file:
        for line in file:
            (key, value) = line.split(':')
            names_dict[str(key)] = value.rstrip()
    files = get_files(input_path, file_name)
    master_df = create_master_df(input_path,
                                 files, c_size,
                                 data_fields)
    master_df.rename(columns=names_dict, inplace=True)
    master_df.to_csv(output_path + master_output)
    master_df = pd.read_csv(output_path + master_output,
                            low_memory=False)
    master_df = dropping_multiple_ips_asns(input_path, master_df)
    master_df.to_csv(output_path + master_output)


def get_files(input_path, file_name):
    """Getting Files from directory using convention"""
    file_list = []
    for file in os.listdir(input_path):
        if file.startswith(file_name):
            changing_line(file, input_path)
            file_list.append(file)
            print("Creating " + file)
    return file_list


def changing_line(given_file, input_path):
    """This function alters the column names"""
    with open(input_path + given_file, 'r')as file:
        lines = file.read().splitlines()
    lines[0] = lines[0].lower()
    rep = {"domain.ipaddresses": "", "feed": "", "ipaddress": "",
           "ip.": "", "_": "", ".": "", "-": "", "xml": "", "domain": ""}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    lines[0] = pattern.sub(lambda m: rep[re.escape(m.group(0))], lines[0])
    with open(input_path + given_file, 'w')as file:
        file.write('\n'.join(lines))


def create_master_df(input_path, files,
                     c_size, data_fields):
    """Creating DFs for both IP and URL Deepsight Data"""
    df = pd.DataFrame()
    for file in files:
        df_chunk = pd.DataFrame()
        for chunk in pd.read_csv(input_path + file, chunksize=c_size,
                                 usecols=lambda x: x in data_fields,
                                 encoding='utf-8'):
            df_chunk = pd.concat([df_chunk, chunk])

        df = pd.concat([df, df_chunk], sort=False)
    print('This is the length: ', len(df.index))
    return df


def dropping_multiple_ips_asns(input_path, df):
    """Getting rid of multiple IPs and ASNs"""
    print("Dropping multiple IPs and ASNs")
    drop_set = set()
    temp_list = []
    print('Looping through dataframe')
    counter = 0
    print("Length of DF: ", len(df.index))
    for x in range(len(df.index)):
        counter += 1
        ip_addr = str(df['IP_Address'][x])
        asn = str(df['ASN'][x])
        if ip_addr == 'nan':
            drop_set.add(x)
        elif ip_addr[0].isdigit() is False:
            drop_set.add(x)
        elif len(ip_addr) > 15:
            ip_list = df['IP_Address'][x].split(',')
            for y in ip_list:
                temp_rows = df.iloc[x].copy()
                temp_rows['IP_Address'] = y
                temp_rows['ASN'] = -1
                temp_list.append(temp_rows)
            drop_set.add(x)
        elif asn == 'nan':
            drop_set.add(x)
        elif len(asn) > 12:
            drop_set.add(x)

    df.drop(drop_set, inplace=True)
    temp_df = pd.DataFrame(temp_list)
    temp_df.reset_index(drop=True, inplace=True)
    start_time = time.time()
    temp_df = resolve_asn(input_path, temp_df)
    print(time.time() - start_time)
    df = df.append(temp_df)
    df['ASN'] = pd.to_numeric(df['ASN'], downcast='integer')
    df.sort_values(by=['ASN', 'Source_Date'], inplace=True)
#    df.reset_index(drop=True, inplace=True)
    return df


def resolve_asn(input_path, df):
    """Resolving the ASN when it is Zero"""
    print('Resolving ASN')
    geo_path = input_path + '/geolite_ordered.csv'
    geo_df = pd.read_csv(geo_path)
    df = sorting_by_address(df)
    print('Back to resolving')
    geo_counter = 0
    total_matches = 0
    for x in range(len(df.index)):
        match = False
        while(match is False and geo_counter < len(geo_df.index) -1):
            ip_sep = df.iloc[x]['IP_List']
            geo_ip_sep = geo_df.iloc[geo_counter]['IP_List'].strip('][').split(', ')
            is_ip_bigger = comparing_ip_size(ip_sep, geo_ip_sep)
            if is_ip_bigger:
                geo_counter += 1
            elif(ipaddress.ip_address(df.iloc[x]['IP_Address']) in
                 ipaddress.ip_network(geo_df.iloc[geo_counter]['IP_CIDR'])):
                df.at[x, 'ASN'] = geo_df.iloc[geo_counter]['ASN']
                match = True
                total_matches += 1
            else:
                match = True

    print('Total Matches: ', total_matches)
    df.drop(columns=['IP_List'], inplace=True)
    return df


def comparing_ip_size(ip1, ip2):
    """Checking the IP Size"""
#    print('Comparing IP Size', ip1, ip2)
    counter = 0
    while counter < 4:
        if int(ip1[counter]) < int(ip2[counter]):
            return False
        elif int(ip1[counter]) > int(ip2[counter]):
            return True
        counter += 1
    return False


def sorting_by_address(df):
    """Sorting By IP Address"""
    print('In Sorting By Address')
    ips = []
    for x in range(len(df.index)):
        ip_list = df.iloc[x]['IP_Address'].split('.')
        for y in range(0, 4):
            ip_list[y] = int(ip_list[y])
        ips.append(ip_list)
    df['IP_List'] = ips
    df.sort_values(by=['IP_List'], inplace=True)
    return df
