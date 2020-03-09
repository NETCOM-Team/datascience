from random import getrandbits
from ipaddress import IPv4Address
import json


#this will generate a list of 1000 random ip addresses for which to test the API

def random_ip():
	bits = getrandbits(32) # generates an integer with 32 random bits
	addr = IPv4Address(bits) # instances an IPv4Address object from those bits
	addr_str = str(addr) # get the IPv4Address object's string representation
	return addr_str
	
def main():
	ip_list = []
	for i in range(1,1000):
		ip = random_ip()
		ip_list.append(ip)
	print(json.dumps(ip_list))
main()
