#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 08:47:11 2020

@author: jacksonbrietzke
"""
import shutil
import re


def main():
    print("Programming Running")
    files = ['../data2/Deepsight IP Malware Nov_Dec 2019.csv',
             '../data2/Deepsight IP Reputation CNC Nov 2019.csv']
    for file in files:
        changing_line(file)


def changing_line(file):
    from_file = open(file)
    line = from_file.readline()
    line = line.lower()
    print(line)
    rep = {"feed": "", "ipaddress": "", "ip.": "", "_": "", ".": "", "-": ""}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    line = pattern.sub(lambda m: rep[re.escape(m.group(0))], line)
    print(line)
    to_file = open(file, "w")
    to_file.write(line)
    shutil.copyfileobj(from_file, to_file)
    from_file.close()
    to_file.close()


main()
