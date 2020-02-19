#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:52:06 2020

@author: jacksonbrietzke
@author: rajsingh
This is the driver file for the project
"""

import ASN
import os
import time

def main():
    start_time = time.time()
    inputPath = 'data/'
    outputPath = 'master'
    if not os.path.isdir(inputPath):
        os.mkdir(inputPath)
    if not os.path.isdir(outputPath):
        os.mkdir('Data/output')
    if not os.path.exists('master/geolite_lookup.csv'):
        ASN.Creating_IP_ASNs.create_geolite_lookup(inputPath, outputPath)

    ASN.Aggregating_Deepsight.creating_files(inputPath, outputPath)
#    ASN.Creating_IP_ASNs.creating_ip_asn_lookups(inputPath, outputPath)
    ASN.Creating_ASN_Objs.creating_asns(outputPath)
#    ASN.Appending_Badness_Cleaned.append_badness()
    print("--- %s seconds ---" % (time.time() - start_time))

main()
