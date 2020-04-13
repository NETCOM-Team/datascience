"""
Created on Tue Feb 18 01:15:43 2020

@author: jacksonbrietzke
"""

""" Cleans the geolite database and translates IP addresses to CIDR notation for visualization use

"""

import ipaddress
import time
import pandas as pd


""" Reads the geolite database and creates CIDR notation IP addresses for visualizations purposes

Args
-------
    input_path (str): the path to the geolite database
"""
def cleaning_geolite(input_path: str):
    """Main Function for creating CIDRs."""
    start_time = time.time()
    geo_input_path = input_path + 'geolite_original.csv'
    geo_df = pd.read_csv(geo_input_path)
    last_hosts_list = []
    drop_set = set()
    for number in range(len(geo_df.index)):
        if geo_df['ASN'][number] == '-':
            drop_set.add(number)
    geo_df.drop(drop_set, inplace=True)
    for index, row in geo_df.iterrows():
        network = ipaddress.ip_network(row['IP_CIDR'])
        last_hosts_list.append(network[-1])
    ips_separated = []
    for ip in last_hosts_list:
        temp_list = str(ip).split('.')
        for place in range(0, 4):
            temp_list[place] = int(temp_list[place])
        ips_separated.append(temp_list)
    geo_df['IP_List'] = ips_separated
    geo_df.sort_values(by=['IP_List'], inplace=True)
    geo_df.to_csv(input_path + 'geolite_ordered.csv')
    print("--- %s seconds ---" % (time.time() - start_time))
