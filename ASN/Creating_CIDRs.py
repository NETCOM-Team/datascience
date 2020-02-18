#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 01:15:43 2020

@author: jacksonbrietzke
"""

import ipaddress
import pandas as pd
import time

def main():
    start_time = time.time()
    inputPath = '../Temp'
    inputPath = inputPath + '/geolite.csv'
    geo_df = pd.read_csv(inputPath)
    last_hosts_list = []
    print('A')
    for index, row in geo_df.iterrows():
#        n = ipaddress.IPv4Network('10.10.128.0/17')
#        first, last = n[0], n[-1]
        n = ipaddress.ip_network(row['IP_CIDR'])
#        all_hosts = list(n.hosts())
        last_hosts_list.append(n[-1])
    ips_separated = []
    print('B')
    for x in last_hosts_list:
        temp_list = str(x).split('.')
        for y in range(0,4):
            temp_list[y] = int(temp_list[y])
        ips_separated.append(temp_list)
    geo_df['IP_List'] = ips_separated
    print('C')
    geo_df.sort_values(by=['IP_List'], inplace=True)
    geo_df.to_csv('../Temp/geolite3.csv')
    print("--- %s seconds ---" % (time.time() - start_time))
    
main()