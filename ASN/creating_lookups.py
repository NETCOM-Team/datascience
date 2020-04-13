"""
@author: jacksonbrietzke
"""
import ipaddress
import pandas as pd

"""
    This file looks up which IPs are in which ASN's and outputs them to geolite_lookup.csv
"""

""" driver function for creating the geolite lookup

Args
-------
    input_path (str): the path to the original Geolite database file
    output_path (str): the path to output the new Geolite look with less columns for our use

"""
def creating_ip_asn_lookups(input_path: str, output_path: str):
    """Creating ASN lookups for ASN Objs to use"""
    print("Creating IP/ASN Lookups")
    create_geolite_lookup(input_path, output_path)


""" Uses the Geolite database to lookup which IP's belong to which ASN's


Args
-------
    input_path (str): the path to the original Geolite database file
    output_path (str): the path to output the new Geolite look with less columns for our use

"""
def create_geolite_lookup(input_path: str , output_path: str):
    """Creating Geolite csv to find IP/ASN mapping"""
    print("Creating Geolite Lookup")
    max_asn = 600000
    geolite_input_file = input_path + 'geolite_original.csv'
    geolite_output_file = output_path + 'geolite_lookup.csv'
    geo_df = pd.read_csv(geolite_input_file)
    geo_df = geo_df.drop(geo_df.columns[[0, 1, 4]], axis=1)
    geo_df = geo_df[geo_df.ASN != '-']
    geo_df = geo_df.astype({'ASN': int})
    geo_df.sort_values(by='ASN', inplace=True)
    asn_list = []
    for number in range(0, max_asn):
        asn_list.append([number, 0])
    current_asn = 0
    current_ip_total = 0
    for index, row in geo_df.iterrows():
        if int(row['ASN']) == current_asn:
            current_ip_total += ipaddress.ip_network(row['IP_CIDR']).num_addresses
        else:
            asn_list[current_asn] = [current_asn, current_ip_total]
            current_asn = int(row['ASN'])
            current_ip_total = ipaddress.ip_network(row['IP_CIDR']).num_addresses
    asn_list[current_asn] = [current_asn, current_ip_total]
    df = pd.DataFrame(asn_list, columns=['ASN', 'Total_IPs'])
    df.to_csv(geolite_output_file)
