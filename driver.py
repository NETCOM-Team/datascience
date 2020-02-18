#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:52:06 2020

@author: jacksonbrietzke
This is the driver file for the project
"""

import ASN
import os
import time

def main():
    start_time = time.time()
    inputPath = 'data'
    outputPath = 'master'
    if not os.path.isdir(inputPath):
        os.mkdir(inputPath)
    if not os.path.isdir(outputPath):
        os.mkdir(outputPath)
    ASN.Aggregating_Deepsight.creating_files(inputPath, outputPath)
#    ASN.Creating_IP_ASNs.creating_ip_asn_lookups(inputPath, outputPath)
    ASN.Creating_ASN_Objs.creating_asns(outputPath)
    print("--- %s seconds ---" % (time.time() - start_time))
    
main()
