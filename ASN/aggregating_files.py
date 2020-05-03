"""
@author jacksonbrietzke
@author rajsingh
"""

""" This file contains functions which take in all of the Deepsight data, aggregate it, rename the columns, and output the
    processed data to a new, cleaner file called MASTER.csv. It will create 1-n versions of master (MASTER1, MASTER2, ..., MASTERn)
    based on how many consecutive data sets have been ingested.

"""

import os
import ipaddress
import re
import time
import pandas as pd
from . import creating_asn_objects

""" Aggregates the Deepsight data and outputs the new MASTER.csv (or MASTER2, MASTER3, ... , MASTERn.csv)
    based on how many times this program has been run (n) as part of the rolling ingestion process.

Args
-----
    input_path (str): The input path of the Deepsight files to aggregate
    output_path (str): The output path which signifies where the aggregated MASTER.csv will be placed

"""
def creating_files(input_path: str, output_path: str):
    """Creating Files."""
    print("Creating Files")
    master_output = '/MASTER.csv'
    """ Check whether or not this is part of the rolling ingest and not the initial run of the program
        If it is, change the name of the master version which is being output"""
    redis_instance = creating_asn_objects.start_redis()
    if redis_instance.exists('master_version'):
        print('inside creating_files;')
        master_version = int(redis_instance.get('master_version').decode('utf-8'))
        print('master version: {}'.format(master_version))
        print('master version type: {}'.format(type(master_version)))
        if master_version > 1:
            print('master version bigger than 1?: {}'.format(master_version))
            master_output = '/MASTER' + str(master_version) + '.csv'
            creating_asn_objects.stop_redis(redis_instance)
    else:
        creating_asn_objects.stop_redis(redis_instance)

    file_name = "Deepsight"
    files = []
    col_names_dict = {}
    c_size = 1000

    """ open the data fields and names dict; data_fields.txt signifies
        the naming convention of the columns in the original files and
        names_dict.txt will be what they will be renamed to (so that
        they are easier to understand and work with"""
    with open(input_path + 'deepsight_fields.txt') as file:
        data_fields = file.read().splitlines()
    with open(input_path + 'deepsight_dict.txt') as file:
        for line in file:
            (key, value) = line.split(':')
            col_names_dict[str(key)] = value.rstrip()
    files = get_files(input_path, file_name)
    """ create master df, resolve ASN's, rearrange df,
        and output to MASTER(1..n).csv
    """
    master_df = create_master_df(input_path,
                                 files, c_size,
                                 data_fields)
    master_df.rename(columns=col_names_dict, inplace=True)
    master_df.to_csv(output_path + master_output)
    master_df = pd.read_csv(output_path + master_output,
                            low_memory=False)
    master_df = dropping_multiple_ips_asns(input_path, master_df)
    master_df.to_csv(output_path + master_output)

""" This function collects the Deepsight files and returns a list of all of them
    with newly named and parsed columns.

Args
-------
    input_path (str): The directory containing the Deepsight files to aggregate
    file_name (str): path to file to rename

Returns
-------
    file_list (list): The new list of files with cleaner columnn names
"""
def get_files(input_path: str, file_name: str) -> list:
    """Getting Files from directory using convention"""
    file_list = []
    for file in os.listdir(input_path):
        if file.startswith(file_name):
            """rename the columns into something sensible"""
            changing_line(file, input_path)
            file_list.append(file)
            print("Creating " + file)
    return file_list

"""This function alters the column names and makes them more readable.

Args
-------
    given_file (str): The filename whose columns should be renamed
    input_path (str): The path to 'given_file'

"""
def changing_line(given_file: str, input_path: str):
    """This function alters the column names"""
    with open(input_path + given_file, 'r') as file:
        lines = file.read().splitlines()
    lines[0] = lines[0].lower()
    """regular expressions to match column name patterns"""
    rep = {"domain.ipaddresses": "", "feed": "", "ipaddress": "",
           "ip.": "", "_": "", ".": "", "-": "", "xml": "", "domain": ""}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    lines[0] = pattern.sub(lambda m: rep[re.escape(m.group(0))], lines[0])
    with open(input_path + given_file, 'w')as file:
        file.write('\n'.join(lines))

""" This function creates the new, renamed MASTER dataframe by reading it in
    chunks at a time

Args
-------
    input_path (str): The path to the MASTER dataframe
    files (list): the list of files to condense into MASTER
    c_size (int): the size of the chunks
    data_fields (list): column names

Returns
-------
    df (pd.DataFrame): the finished MASTER dataframe with newly named columns
"""
def create_master_df(input_path: str, files: list,
                     c_size: int, data_fields: list) -> pd.DataFrame:
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

""" This function drops multiple IP / ASN entries. For example,
    if an event doesn't have an IP, it gets dropped. If the ASN is
    out of range, it gets dropped, etc. It returns a data frame with
    only valid, resolved ASNs (using resolve_asn) sorted by date and
    ASN number

Args
-------
    input_path (str): path to the geolite database to resolve ASN's
    df (pd.Dataframe): the MASTER data frame passed in containing Event/ASN info

Returns
-------
    df (pd.Dataframe): The dataframe with the updated ASN/Event info
"""
def dropping_multiple_ips_asns(input_path: str, df: pd.DataFrame) -> pd.DataFrame:
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
        """drop unnecessary / invalid ASN's"""
        if ip_addr == 'nan':
            drop_set.add(x)
        elif ip_addr[0].isdigit() is False:
            drop_set.add(x)
        elif len(ip_addr) > 15:
#            This is commented out for Aaron's part
#            ip_list = df['IP_Address'][x].split(',')
#            for y in ip_list:
#                temp_rows = df.iloc[x].copy()
#                temp_rows['IP_Address'] = y
#                temp_rows['ASN'] = -1
#                temp_list.append(temp_rows)
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
    return df

""" This function resolves an ASN and checks which IP addresses
    are associated with it. It maps each ASN to the multiple
    IP addresses that might be associated with it.

Args
-------
    input_path (str): path to the geolite database to resolve ASN's
    df (pd.Dataframe): the MASTER data frame passed in containing Event/ASN info

Returns
-------
    df (pd.Dataframe): The dataframe with the updated ASN/Event info
"""
def resolve_asn(input_path, df) -> pd.DataFrame:
    """Resolving the ASN when it is Zero"""
    print('Resolving ASN')
    geo_path = input_path + '/geolite_ordered.csv'
    geo_df = pd.read_csv(geo_path)
    df = sorting_by_address(df)
    print('Back to resolving')
    geo_counter = 0
    total_matches = 0
    """get valid IP's for each ASN"""
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

"""Compares two IPv4 addresses

Args
-------
    ip1 (str): IP address 1
    ip2 (str): IP address 2

Returns
-------
    bool: True or false based on whether or not ip1 > ip2
"""
def comparing_ip_size(ip1, ip2) -> bool:
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

"""sorts our Event/ASN dataframe by IP address

Args
-------
    df (pd.DataFrame): the dataframe to be sorted

Returns
-------
    df (pd.DataFrame): the dataframe sorted by IP address
"""
def sorting_by_address(df) -> pd.DataFrame:
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
