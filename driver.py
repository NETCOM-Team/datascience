#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:52:06 2020

@author: jacksonbrietzke
This is the driver file for the project
"""

import ASN
ASN.Aggregating_Deepsight.creating_files()
ASN.Cleaning_Master.cleaning_master()
#ASN.Creating_IP_ASNs.creating_ip_asn_lookups()
ASN.Creating_ASN_Objs.creating_asns()
