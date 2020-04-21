#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 16:57:40 2020

@author: jacksonbrietzke
"""
import pandas as pd


def main():
    print('Starting program')
    input_path = 'data/tornodes.csv'
    output_path = 'master/'
    tor_dict = {}
    with open('data/tor_fields.txt') as file:
        tor_fields = file.read().splitlines()
    with open('data/tor_dict.txt') as file:
        for line in file:
            (key, value) = line.split(':')
            tor_dict[str(key)] = value.rstrip()
    print(tor_dict, tor_fields)
    files = ['Tornodes.csv']
    df = create_master_df('./', files, 1000, tor_fields)
    df.rename(columns=tor_dict, inplace=True)
    df.to_csv(output_path + 'tor.csv')
    print(df)


class Tor:
    def __init__(self, ip, asn, country_code, first_seen):
        print('Born')
        error_value = 'None'
        try:
            self.ip = str(ip)
        except ValueError:
            self.ip = error_value
        try:
            self.asn = int(asn)
        except ValueError:
            self.asn = error_value
        try:
            self.country_code = str(country_code)
        except ValueError:
            self.country_code = error_value
        try:
            self.first_seen = str(first_seen)
        except ValueError:
            self.first_seen = error_value


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

main()
