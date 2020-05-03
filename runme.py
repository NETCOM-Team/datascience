import os
import time
import redis

def main():
    start_time = time.time()
    input_path = 'data/'
    output_path = 'master/'
    setup_directories(input_path, output_path)
    #ASN.aggregating_files.creating_files(input_path, output_path)
    #ASN.creating_asn_objects.creating_asns(output_path, input_path)

def setup_directories(input_path: str, output_path: str):
    if not os.path.isdir(input_path):
        os.mkdir(input_path)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    #if not os.path.exists(output_path + 'geolite_lookup.csv'):
      #  ASN.creating_lookups.create_geolite_lookup(input_path, output_path)
    #if not os.path.exists(input_path + 'geolite_ordered.csv'):
    #    ASN.ordering_geolite.cleaning_geolite(input_path)

main()
