#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 01:15:43 2020

@author: jacksonbrietzke
"""

import ipaddress
import time
import pandas as pd


def main():
    """Main Function for creating CIDRs."""
    start_time = time.time()
    input_path = '../data'
    input_path = input_path + '/geolite_original.csv'
    geo_df = pd.read_csv(input_path)
    last_hosts_list = []
    drop_set = set()
    print('A')
    for number in range(len(geo_df.index)):
        if geo_df['ASN'][number] == '-':
            drop_set.add(number)
    geo_df.drop(drop_set, inplace=True)
    for index, row in geo_df.iterrows():
        #        n = ipaddress.IPv4Network('10.10.128.0/17')
        #        first, last = n[0], n[-1]
        network = ipaddress.ip_network(row['IP_CIDR'])
#        all_hosts = list(n.hosts())
        last_hosts_list.append(network[-1])
    ips_separated = []
    print('B')
    for ip in last_hosts_list:
        temp_list = str(ip).split('.')
        for place in range(0, 4):
            temp_list[place] = int(temp_list[place])
        ips_separated.append(temp_list)
    geo_df['IP_List'] = ips_separated
    print('C')
    geo_df.sort_values(by=['IP_List'], inplace=True)
    geo_df.to_csv('../Temp/geolite3.csv')
    print("--- %s seconds ---" % (time.time() - start_time))


main()
