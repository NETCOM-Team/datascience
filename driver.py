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

    redis_instance = ASN.Creating_ASN_Objs.start_redis()
    if os.path.exists('master/serialized_before'):
        redis_instance.incr('master_version')
    else:
        redis_instance.set('master_version', 1)
    
    input_path = 'data/test2'
    output_path = 'master/'
    if not os.path.isdir(input_path):
        os.mkdir(input_path)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    if not os.path.exists(output_path + 'geolite_lookup.csv'):
        ASN.Creating_IP_ASNs.create_geolite_lookup(input_path, output_path)

    ASN.Aggregating_Deepsight.creating_files(input_path, output_path)
#    ASN.Creating_IP_ASNs.creating_ip_asn_lookups(input_path, output_path)
    ASN.Creating_ASN_Objs.creating_asns(output_path)
#    ASN.Appending_Badness_Cleaned.append_badness()
    ASN.Creating_ASN_Objs.stop_redis(redis_instance)
    print("--- %s seconds ---" % (time.time() - start_time))


main()
