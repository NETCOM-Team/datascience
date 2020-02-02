import os
import signal
from subprocess import check_output
import redis

#for now this script assumes that redis-server is running in the background
#later I will make it so that it does appropriate port/socket opening and closing etc/

#os.system("redis-server &")
#print('redis running')

r = redis.Redis(host='localhost', port=6379, db=0)

#issue is that in redis sorted sets, you can't have strings as the values for the keys.
#this is a problem because we can't store IP's as floats.
#could possibly circumvent this by having the keys  being asn:ip and have the value for that key being a 0 or 1?
#might also be helpful in scoring
asn_dict = {
    394695: '1.1.1.1',
    1720: '2.2.2.2',
    9498: '3.3.3.3',
    4809: '4.4.4.4'
}

#add ASN's and IP's to redis sorted set called asn_object_dict
for asn, ip in asn_dict.items():
    r.zadd('asn_object_dict', {asn: 1})

for key, val in r.zrevrange('asn_object_dict', 0, len(asn_dict), 'withscores'):
    print(key, val)

#os.system("ps aux | grep 6379 | awk '{print $2}' | xargs kill -9")
