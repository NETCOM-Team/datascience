print("in driver.py")

import os
import time
from ASN import creating_asn_objects, ordering_geolite, creating_lookups
import redis


def main():
    """Driver function for ASN Program"""
    start_time = time.time()
    input_path = 'data/'
    output_path = 'master/'
    redis_instance = setup_redis()
    setup_directories(input_path, output_path)
    creating_asn_objects.creating_files(input_path, output_path)
    creating_asn_objects.creating_asns(output_path, input_path)
    creating_asn_objects.stop_redis(redis_instance)
    print("--- %s seconds ---" % (time.time() - start_time))


""" Does some error checking with directories to make sure the program runs properly
Args
-------
    input_path (str): input path to the data files (Deepsight files)
    output_path (str): where to write all of the output CSV's to
"""
def setup_directories(input_path: str , output_path: str):
    if not os.path.isdir(input_path):
        os.mkdir(input_path)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    if not os.path.exists(output_path + 'geolite_lookup.csv'):
        creating_lookups.create_geolite_lookup(input_path, output_path)
    if not os.path.exists(input_path + 'geolite_ordered.csv'):
        ordering_geolite.cleaning_geolite(input_path)


""" Starts a redis instance and checks whether or not this is a rolling ingest.
    If it is; it will increment the master version that should be outputted (1..n)
Returns
-------
    redis_instance (redis.StrictRedis): the connection to the redis database
"""
def setup_redis() -> redis.StrictRedis:
    redis_instance = creating_asn_objects.start_redis()
    if os.path.exists('master/serialized_before'):
        redis_instance.incr('master_version')
    else:
        redis_instance.set('master_version', 1)
    return redis_instance


main()

main()
