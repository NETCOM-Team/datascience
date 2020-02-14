#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:52:06 2020

@author: jacksonbrietzke
This is the driver file for the project
"""

import ASN
import os

def main():
    inputPath = 'Data'
    outputPath = 'Data/Output'
    if not os.path.isdir(inputPath):
        os.mkdir('Data')
    if not os.path.isdir(outputPath):
        os.mkdir('Data/Output')
    ASN.Aggregating_Deepsight.creating_files(inputPath, outputPath)
    #ASN.Cleaning_Master.cleaning_master()
#    ASN.Creating_IP_ASNs.creating_ip_asn_lookups(inputPath, outputPath)
    ASN.Creating_ASN_Objs.creating_asns(outputPath)
    
main()
