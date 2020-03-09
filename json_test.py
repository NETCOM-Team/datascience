import ASN
import json
import redis

r = redis.Redis(host='localhost', port=6379)
x = ASN.Creating_ASN_Objs.ASN(1234)
print(json.dumps(x.__dict__, indent=4))
r.set(x.as_number, json.dumps(x.__dict__))
print(r.get(x.as_number))
print(json.loads(json.dumps(x.__dict__)))

