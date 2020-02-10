#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 11:03:05 2020

@author: jacksonbrietzke
"""

import os
import subprocess
import ipaddress

def main():
    r = "2"
    x = subprocess.check_output("whois -h whois.radb.net -- '-i origin AS" + r + 
                                "'| grep -Eo '([0-9.]+){4}/[0-9]+'",
                                shell=True).decode("utf-8") 
    x = x.split('\n')[:-1]
    totalIPs = 0
    for y in x:
        print(y)
        try:
            totalIPs += ipaddress.ip_network(y).num_addresses
        except Exception as e: 
            print(e)
    print(totalIPs)
if __name__ == "__main__":
    main()
