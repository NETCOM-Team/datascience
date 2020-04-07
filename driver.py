#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:52:06 2020

@author: jacksonbrietzke
@author: rajsingh
This is the driver file for the project yes
"""

import os
import time
import ASN


def main():
    """Driver function for ASN Program"""
    start_time = time.time()
    input_path = 'data/'
    output_path = 'master/'
    redis_instance = setup_redis()
    setup_directories(input_path, output_path)
    ASN.aggregating_files.creating_files(input_path, output_path)
    ASN.creating_asn_objects.creating_asns(output_path)
    ASN.creating_asn_objects.stop_redis(redis_instance)
    print("--- %s seconds ---" % (time.time() - start_time))


def setup_directories(input_path, output_path):
    if not os.path.isdir(input_path):
        os.mkdir(input_path)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    if not os.path.exists(output_path + 'geolite_lookup.csv'):
        ASN.creating_lookups.create_geolite_lookup(input_path, output_path)
    if not os.path.exists(input_path + 'geolite_ordered.csv'):
        ASN.ordering_geolite.cleaning_geolite(input_path)


def setup_redis():
    redis_instance = ASN.creating_asn_objects.start_redis()
    if os.path.exists('master/serialized_before'):
        redis_instance.incr('master_version')
    else:
        redis_instance.set('master_version', 1)
    return redis_instance


main()
