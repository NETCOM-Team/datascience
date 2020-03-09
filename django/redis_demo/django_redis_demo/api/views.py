import json
import subprocess
from django.conf import settings
import redis
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,port=settings.REDIS_PORT, db=0)

# @api_view(['GET'])
# def datascience_greeting(request, *args, **kwargs):
#     response = {'datascience': 'welcome'}
#     return Response(response,200)

@api_view(['GET', 'POST'])
def manage_items(request, *args, **kwargs):
    if request.method == 'GET' and request.path=="/asn":
        #get the body of the json-submitted request
        body = json.loads(request.body)
        #retrieve the value from redis with the asn requested
        response = getASNdetails(body["asn"])

        return Response(response,200)

    if request.method == 'GET' and request.path == "/ip":
        body = json.loads(request.body)
        response = {}

        for ip in body["ip"]:
            asn = resolve_asn(ip)
            # resolve the ip's passed in the body to their respective asn's
            asn_object = getASNdetails(asn)
            print(asn_object)
            response[ip] = asn_object

        print(response)
        return Response(response,200)



def resolve_asn(ip):
    print(ip)
    # create an asnList to store our list of dictionarires retrieved from redis
    asnList = []

    # perform a whois lookup on each ip address to get its ASN; swap out once we have the appropriate .csv
    command = "whois -h whois.radb.net " + ip + "| grep 'origin:' | awk '{print $2}' | head -n 1 | cut -d 'S' -f 2"
    asn = subprocess.check_output(command,shell=True).decode("utf-8")
    # strip off the newline that is appended to the subprocess command.
    asn = asn.rstrip()
    #create a list of these asn's so we can pass them to getASNdetails
    asnList.append(asn)

    return asnList

def getASNdetails(asnList):
    response_list = []
    for asn in asnList:
        # redis returns a serialized json object
        serialized_asn = redis_instance.get(asn)

        # if there is not an asn object for this asn it returns None
        if serialized_asn == None:
            # create a dictionary to store our single asn object
            risk_dictionary = {}
            risk_dictionary[asn] = "no known score"
            response_list.append(risk_dictionary)
        else:
            deserialized = json.loads(serialized_asn)
            risk_dictionary = {}
            risk_dictionary[asn] = deserialized
            response_list.append(risk_dictionary)

    response = {
            "asns" : response_list
    }

    return response







        # items = {}
        # count = 0
        # for key in redis_instance.keys("*"):
        #     if count < 100:
        #         items[key.decode("utf-8")] = redis_instance.get(count)

        #         count += 1
        # response = {
        #     'count': count,
        #     'msg': f"Found {count} items.",
        #     'items': items
        # }
        # return Response(response, status=200)

        # elif request.method == 'POST':
        #     item = json.loads(request.body)
        #     key = list(item.keys())[0]
        #     value = item[key]
        #     redis_instance.set(key, value)
        #     response = {
        #         'msg': f"{key} successfully set to {value}"
        #     }
        #     return Response(response, 201)





# @api_view(['GET', 'PUT', 'DELETE'])
# def manage_item(request, *args, **kwargs):
#     if request.method == 'GET':
#         if kwargs['key']:
#             value = redis_instance.get(kwargs['key'])
#             if value:
#                 response = {
#                     'key': kwargs['key'],
#                     'value': value,
#                     'msg': 'success'
#                 }
#                 return Response(response, status=200)
#             else:
#                 response = {
#                     'key': kwargs['key'],
#                     'value': None,
#                     'msg': 'Not found'
#                 }
#                 return Response(response, status=404)
#     elif request.method == 'PUT':
#         if kwargs['key']:
#             request_data = json.loads(request.body)
#             new_value = request_data['new_value']
#             value = redis_instance.get(kwargs['key'])
#             if value:
#                 redis_instance.set(kwargs['key'], new_value)
#                 response = {
#                     'key': kwargs['key'],
#                     'value': value,
#                     'msg': f"Successfully updated {kwargs['key']}"
#                 }
#                 return Response(response, status=200)
#             else:
#                 response = {
#                     'key': kwargs['key'],
#                     'value': None,
#                     'msg': 'Not found'
#                 }
#                 return Response(response, status=404)

#     elif request.method == 'DELETE':
#         if kwargs['key']:
#             result = redis_instance.delete(kwargs['key'])
#             if result == 1:
#                 response = {
#                     'msg': f"{kwargs['key']} successfully deleted"
#                 }
#                 return Response(response, status=404)
#             else:
#                 response = {
#                     'key': kwargs['key'],
#                     'value': None,
#                     'msg': 'Not found'
#                 }
#                 return Response(response, status=404)
