"""
@author: jacksonbrietzke
@author: rajsingh
"""


""" This file defines the classes for Events and ASN Objects
    Various functionality to perform operations on events and the
    ASN objects is also provided. Each event represents one row in the
    Symantec deepsight data and each ASN object can have multiple
    events.
"""

import json
import csv
import os
import redis
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import ASN as AL
import pprint

class Event:

    """
    A class used to represent a threat event, or a row in the Symantec data feeds.
    All of the attributes listed here are not all of the attributes in the data feeds.

    Attributes
    ----------
    event_id : str
        a string representing the threat event's ID
    ip_address : str
        the IP address associated with the event
    confidence : str
        the confidence rating of the event
    hostility : int
        the hostility rating of the event
    reputation_rating: int
        the reputation rating of the event.

    Methods
    -------
    create_score(self) -> int
        Returns the score of the event; the score represents a weighting
        which gives us an idea of how "bad" the event is
    """

    def __init__(self, event_id, ip_address, confidence,
                 hostility, reputation_rating):
        self.event_id = event_id
        self.ip_address = ip_address
        try:
            self.confidence = int(confidence)
        except ValueError:
            self.confidence = 0
        try:
            self.hostility = int(hostility)
        except ValueError:
            self.hostility = 0
        try:
            self.reputation_rating = int(reputation_rating)
        except ValueError:
            self.reputation_rating = 0
        self.score = self.create_score()

    def create_score(self) -> float:
        """Creating Score for Event."""
        temp_score = self.hostility + self.confidence + self.reputation_rating
        if self.hostility == 0:
            temp_score = temp_score / 15
        else:
            temp_score = temp_score / 20
        return temp_score


class Tor:
    def __init__(self, ip, asn, country_code, first_seen):
        error_value = False
        try:
            self.ip = str(ip)
        except ValueError:
            self.ip = error_value
        try:
            self.asn = int(asn)
        except ValueError:
            self.asn = error_value
        try:
            self.country_code = str(country_code)
        except ValueError:
            self.country_code = error_value
        try:
            self.first_seen = str(first_seen)
        except ValueError:
            self.first_seen = error_value


class ASN:

    """
    A class used to represent an ASN object.
    An ASN object is compromised of multiple Events and other
    attributes we'ved added for our analysis.

    Attributes
    ----------
    as_number : str
        The ASN number
    events_list : list
        The list of Event objects that an ASN has.
    score : float
        the score of the ASN (sum of all event scores)
    total_ips : int
        total number of IP's in the ASN
    badness: float
        the badness rating of the ASN.
    has_events: bool
        Signifies whether or not the ASN's events list is empty
    ev_centrality: float
        marks the ASN's eigenvector centrality

    Methods
    -------
    given_asn(cls, as_number) -> cls
        Initializes an instance of the ASN object with the given ASN number
    create_score(self) -> int
        Returns the score of the event; the score represents a weighting
        which gives us an idea of how "bad" the event is
    set_total_ips(self):
        initializes the number of IP's in the ASN
    create_badness(self):
        sets the badness score of the ASN
    set_ev_centrality(self, ev_centrality):
        sets the eigenvector centrality of the ASN object with respect
        to other objects in the graph
    serialize_asn(asn_obj)
        static method with serializes an ASN objects (which is a complex object)
        for storage in, say, a database
    """

    def __init__(self, as_number):
        """Initializing Instance."""
        try:
            self.as_number = int(float(as_number))
        except ValueError:
            self.as_number = False
        self.events_list = []
        self.tor_list = []
        self.score = 0
        self.total_ips = 0
        self.badness = 0
        self.has_events = False
        self.ev_centrality = 0

    @classmethod
    def given_asn(cls, as_number: int) -> object:
        """Initializing Instance with ASN."""
        return cls(as_number)

    def create_score(self):
        """Creating ASN score."""
        temp_score = 0
        for event in self.events_list:
            temp_score += event.score
        self.score = temp_score

    def set_total_ips(self):
        """Setting total IPs for ASN."""
        if self.total_ips == 0:
            self.total_ips = 256

    def create_badness(self):
        """Creating badness score for ASN."""
        self.badness = self.score / self.total_ips

    def set_ev_centrality(self, ev_centrality: tuple):
        """Setting EV Centrality for ASN."""
        self.ev_centrality = ev_centrality[1]

    @staticmethod
    def serialize_asn(asn_obj: object) -> str:
        """Static method for Serializing ASN."""
        serialized_events = []
        serialized_tor = []
        for event in asn_obj.events_list:
            serialized_events.append(event.__dict__)
        for tor in asn_obj.tor_list:
            serialized_tor.append(tor.__dict__)
        asn_obj.events_list = json.dumps(serialized_events)
        asn_obj.tor_list = json.dumps(serialized_tor)
        return json.dumps(asn_obj.__dict__, sort_keys=True, cls=PandasEncoder)

    @staticmethod
    def set_asn_attrs(asn_obj: object, badness: float, ev_centrality: float,
                      events_list: list, tor_list: list, has_events: bool,
                      score: float, total_ips: int) -> object:

        """sets the attributes of an ASN object"""
        asn_obj.badness = badness
        asn_obj.ev_centrality = ev_centrality
        asn_obj.events_list = events_list
        asn_obj.tor_list = tor_list
        asn_obj.has_events = has_events
        asn_obj.score = score
        asn_obj.total_ips = total_ips
        return asn_obj


class PandasEncoder(json.JSONEncoder):
    """
    This is a class which encodes Pandas objects for serialization.
    Redis doesn't like storing Numpy integers, so this class encodes
    them as normal data types for storage in the Redis db

    Attributes
    ----------
    None

    Methods
    -------
    default(self, obj)
        returns the custom encoding of the object with the storable
        data types
    """

    """Custom encoder for Redis."""
    def default(self, obj: object) -> object:
        if isinstance(obj, np.int64):
            obj = int(obj)
        elif isinstance(obj, np.float64):
            obj = float(obj)
        else:
            obj = super(PandasEncoder, self).default(obj)
        return obj

class PandasDecoder(json.JSONDecoder):

    """
    This is a class which decodes the custom encoding specified in
    PandasEncoder.

    Attributes
    ----------
    None

    Methods
    -------
    object_hook(self, obj) -> obj
        returns the custom encoding of the object with the storable
        data types
    """

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj: object) -> object:
        obj['events_list'] = json.loads(obj['events_list'])
        obj['tor_list'] = json.loads(obj['tor_list'])
        return obj


""" Creates the ASN objects from the threat intelligence data. New objects are initialized
    if this is the first time 'driver.py' is being run, otherwise the existing objects
    stored in the redis database are pulled to be updated. This function also writes the output
    to ASN_Scores.csv and MASTER.csv

Args
-----
    output_path (str): The output path which signifies where the aggregated MASTER.csv
    and ASN_Scores.csv will be placed

"""
def creating_asns(output_path: str, input_path: str):
    """Creating ASN Objects."""
    redis_instance = start_redis()
    master_input = output_path + '/MASTER.csv'
    print("Creating ASN Objects")
    if os.path.exists(output_path + '/serialized_before'):
        print('getting from redis')
        asn_objects = get_serialized_list(redis_instance)
        master_input = output_path + 'MASTER'+ redis_instance.get('master_version').decode('utf-8') + '.csv'
        print('NEW MASTER: {}'.format(master_input))
    else:
        print('initalizing from scratch')
        asn_objects = create_max_asn_objects()

    asn_scores_output = output_path + '/ASN_Scores.csv'
    geolite_input = output_path + '/geolite_lookup.csv'
    geolite_df = pd.read_csv(geolite_input)
    master_df = pd.read_csv(master_input, low_memory=False)
    master_df.sort_values(by=['ASN', 'Source_Date'], inplace=True)

    asn_objects = updating_master_and_scores(master_df, asn_objects,
                                             geolite_df, master_input)
    asn_objects = adding_tor(asn_objects, output_path, input_path)
    #fast_mover_asn_viz(3)
    #top_10_badness_viz(asn_objects)
    #creating_asn_evs(asn_objects)
    outputting_asns(asn_scores_output, asn_objects)
    create_marker_serialized(output_path)


""" Creates a directed graph of ASN objects. Nodes are asn numbers and ip addresses.
    This is useful for doing graph based analysis; we use it for calculating
    eigenvector centrality of ASNs.

Args
-----
    asn_obj_list (list): The list of ASN objects to construct the graph

Returns
-------
    graph (nx.Graph): the directed graph of ASN objects / IP addresses

"""
def create_asn_graph(asn_obj_list: list) -> nx.Graph():
    """Creating ASN graph."""
    graph = nx.Graph()
    for obj in asn_obj_list:
        graph.add_node(obj.as_number)
        for event in obj.events_list:
            graph.add_node(event.ip_address)
            graph.add_edge(event.ip_address, obj.as_number)
    return graph


""" Gets a list of eigenvector centrality values from a directed graph

Args
-----
    centrality_struct (dict): The dictionary containing information about the eigenvector
                              centrality of the nodes

Returns
-------
    graph (nx.Graph): the directed graph of ASN objects / IP addresses

"""
def get_eigenvector_centrality(centrality_struct: dict) -> list:
    """Getting the Eigenvector Centraility."""
    ints = []
    for tup in centrality_struct.items():
        if isinstance(tup[0], int):
            ints.append(tup)
    return ints


""" Displays a visual showing the top 10 ASN's by badness score

Args
-----
    asn_object_dict: the list of ASN objects to generate the visual from

"""
def top_10_badness_viz(asn_obj_dict: dict):
    newlist = sorted(asn_obj_dict, key=lambda x: x.badness, reverse=True)
    top_10 = newlist[:10]
    asn_nums = []
    badness = []
    for item in top_10:
        asn_nums.append(item.as_number)
        badness.append(item.badness)
    y_pos = np.arange(len(asn_nums))
    plt.bar(y_pos, badness, align='center', alpha=0.5)
    plt.xticks(y_pos, asn_nums, rotation=90)
    plt.ylabel('Badness Score')
    plt.title("""Top 10 ASN's by Badness""")
    plt.show()
    #plt.savefig(fast_mover.pdf)

""" Displays a visual showing how much more 'bad' an ASN has been getting
    according to historical badness
Args
-----
    asn_number: the list of ASN objects to generate the visual from

"""
def fast_mover_asn_viz(asn_number: int):
    df = pd.read_csv('master/MASTER.csv')
    df = df.loc[df['ASN'] == asn_number]
    dates = [x[0:10] for x in df['Source_Date']]
    scores = list(df['Historical_Score'])
    y_pos = np.arange(len(dates))
    plt.plot(y_pos, scores, '-o')
    plt.xticks(y_pos, dates, rotation=90)
    plt.ylabel('Historical Badness')
    plt.title('Badness over time for ASN {}'.format(asn_number))
    plt.show()
    #plt.savefig(fast_mover.pdf)

""" initializes 600k ASN objects from scratch, used the first time
    'driver.py' is run

Returns
-------
    asn_list (list): the list of freshly initialized ASN objects
"""
def create_max_asn_objects() -> list:
    """Creating Max ASN Objects"""
    max_range = 600000
    asn_list = []
    for number in range(0, max_range):
        asn_list.append(ASN(number))
    return asn_list

""" Updates existing ASN objects and outputs a new MASTER

Args
-----
    master_df (pd.DataFrame): the MASTER data frame to update and write out
    asn_objects (list): the list of ASN objects being updated and being used to
                        update MASTER
    geolite_df (pd.DataFrame): the geolite database used to update IP information about
                                ASN objects
    master_input (str): the path to write the new MASTER to
"""
def updating_master_and_scores(master_df: pd.DataFrame, asn_objects: list,
                               geolite_df: pd.DataFrame, master_input: str) -> list:
    """Updating master and scores."""
    print('Updating Master and Scores')
    asn_chrono_score_list = []
    event_score = []

    for number in range(len(master_df.index)):
        as_number = master_df['ASN'][number]
        temp_event = Event(master_df['ID'][number],
                           master_df['IP_Address'][number],
                           master_df['Confidence'][number],
                           master_df['Hostility'][number],
                           master_df['Reputation_Rating'][number])
        try:
            asn_objects[as_number].events_list.append(temp_event)
        except:
            print("This number is the exception {}".format(as_number))
            print("This is the length of ASN object {}".format(len(asn_objects)))
        event_score.append(temp_event.create_score())
        if asn_objects[as_number].total_ips == 0:
            asn = asn_objects[as_number].as_number
            asn_objects[as_number].total_ips = geolite_df['Total_IPs'][asn]
            asn_objects[as_number].set_total_ips()
        asn_objects[as_number].create_score()
        asn_objects[as_number].create_badness()
        asn_chrono_score_list.append(asn_objects[as_number].badness)
        asn_objects[as_number].has_events = True

    master_df['Event_Score'] = event_score
    master_df['Historical_Score'] = asn_chrono_score_list
    master_df.to_csv(master_input)

    return asn_objects

""" This function pulls down a list of serialized ASN objects from a Redis database
    and deserializes them (for use in the other functions in this file)

Args
-----
    master_df (pd.DataFrame): the MASTER data frame to update and write out
    asn_objects (list): the list of ASN objects being updated and being used to
                        update MASTER
    geolite_df (pd.DataFrame): the geolite database used to update IP information about
                                ASN objects
    master_input (str): the path to write the new MASTER to
"""
def get_serialized_list(redis_instance: redis.StrictRedis) -> list:
    asn_objs = []
    """loop through keys in database to get objects"""
    for key in redis_instance.keys('*'):
        try:
            obj = redis_instance.get(key)
            int(key.decode('utf-8'))
            """deserialize object, next have to deserialize list of event objects"""
            asn_obj_dict = json.loads(obj.decode(errors='ignore'), cls=PandasDecoder)
            if asn_obj_dict['events_list'] != []:
                event_list = []
                for i in range(0, len(asn_obj_dict['events_list'])):
                    event_list.append(Event(asn_obj_dict['events_list'][i]['event_id'],
                        asn_obj_dict['events_list'][i]['ip_address'], asn_obj_dict['events_list'][i]['confidence'],
                        asn_obj_dict['events_list'][i]['hostility'], asn_obj_dict['events_list'][i]['reputation_rating']))
                asn_obj_dict['events_list'] = event_list
            if asn_obj_dict['tor_list'] != []:
                tor_list = []
                for i in range(0, len(asn_obj_dict['tor_list'])):
                    tor_list.append(Tor(asn_obj_dict['tor_list'][i]['ip'],
                                    asn_obj_dict['tor_list'][i]['asn'],
                                    asn_obj_dict['tor_list'][i]['country_code'],
                                    asn_obj_dict['tor_list'][i]['first_seen']))
                asn_obj_dict['tor_list'] = tor_list
            temp_obj = ASN(int(key.decode('utf-8')))
            temp_obj = ASN.set_asn_attrs(temp_obj,
                                         asn_obj_dict['badness'],
                                         asn_obj_dict['ev_centrality'],
                                         asn_obj_dict['events_list'],
                                         asn_obj_dict['tor_list'],
                                         asn_obj_dict['has_events'],
                                         asn_obj_dict['score'],
                                         asn_obj_dict['total_ips'])

            asn_objs.append(temp_obj)
        except KeyError as e:
            print('KeyError: {}'.format(e))
        except ValueError as e:
            print('ValueErrorr: {}'.format(e))
        except redis.exceptions.ResponseError as e:
            print('Redisr: {}'.format(e))
        except AttributeError as e:
            print('AttributeError: {}'.format(e))

    print('done deserializing')
    asn_objs = sorted(asn_objs, key=lambda x: x.as_number)
    print('What is the length of objs: {}'.format(len(asn_objs)))
    return asn_objs

""" This function creates the ASN graph, gets the eigenvector centralities
    and assigns those values to the attributes in the ASN objecs

Args
-----

    asn_objects (list): the list of ASN objects being whose EV centralities
                        are being set
"""
def creating_asn_evs(asn_objects: list):
    """Creating ASN EVs"""
    print('Getting eigenvector centrality')
    event_objects = []
    for obj in asn_objects:
        if obj.has_events:
            event_objects.append(obj)
    graph = create_asn_graph(event_objects)
    ev_centrality = nx.eigenvector_centrality_numpy(graph)
    asn_ev_centralities = get_eigenvector_centrality(ev_centrality)

    i = 0
    for obj in event_objects:
        obj.set_ev_centrality(asn_ev_centralities[i])
        i += 1

""" writes the updated output to ASN_Scores

Args
-----
    output_file (str): directory to write output to
    asn_objects (list): the list of ASN objects being whose EV centralities
                        are being set
"""
def outputting_asns(output_file: str, asn_objects: list):
    """Outputting ASN Scores."""
    print('Outputting ASNs')
    redis_instance = start_redis()
    with open(output_file, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['ASN', 'Score', 'Total_IPs',
                         'Badness', 'Exists', 'EV Centrality'])
        for asn in asn_objects:
            redis_instance.set(asn.as_number, ASN.serialize_asn(asn))
            if(asn.total_ips > 0 or asn.score > 0):
                writer.writerow([asn.as_number, asn.score, asn.total_ips,
                                 asn.badness, True, asn.ev_centrality])
            else:
                writer.writerow([asn.as_number, asn.score, asn.total_ips,
                                 asn.badness, False, asn.ev_centrality])


""" writes out a file which signifies that the current run of driver was
    a rolling ingest

Args
-----
    output_path (str): directory to write the marker file to

"""
def create_marker_serialized(output_path):
    with open(output_path + '/serialized_before', 'w') as f:
        f.write('objects serialized before, this is a new ingest, rolling process')

""" starts a StrictRedis instance

Returns
--------
    redis_instance (redis.StrictRedis): the initialized Redis DB instance
"""
def start_redis() -> redis.StrictRedis:
    redis_host = os.getenv('REDIS_HOST')
    redis_instance = redis.StrictRedis(host=redis_host, port=6379)
    return redis_instance

""" stops a StrictRedis instance

Args
--------
    redis_instance (redis.StrictRedis): the StrictRedis instance to disconnect from
"""
def stop_redis(redis_instance):
    redis_instance.connection_pool.disconnect()


def adding_tor(asn_objects, output_path, input_path):
    print('adding tor nodes to ASN')
    col_names_dict = {}
    tor_path = output_path + 'tor.csv'
    with open(input_path + 'tor_fields.txt') as file:
        data_fields = file.read().splitlines()
    with open(input_path + 'tor_dict.txt') as file:
        for line in file:
            (key, value) = line.split(':')
            col_names_dict[str(key)] = value.rstrip()
    files = AL.aggregating_files.get_files(input_path, 'Tor')
    """ create master df, resolve ASN's, rearrange df,
        and output to MASTER(1..n).csv
    """
    if files:
        tor_df = AL.aggregating_files.create_master_df(input_path,
                                                       files, 1000,
                                                       data_fields)
        tor_df.rename(columns=col_names_dict, inplace=True)
        counter = 0
        for number in range(len(tor_df.index)):
            skipper = False
            try:
                as_number = int(tor_df['ASN'][number])
            except Exception as e:
                skipper = True
                counter += 1
            if(skipper is False):
                temp_tor = Tor(tor_df['IP'][number],
                               tor_df['ASN'][number],
                               tor_df['Country_Code'][number],
                               tor_df['First_Seen'][number])
                asn_objects[as_number].tor_list.append(temp_tor)
        tor_df.to_csv(tor_path)
        print("We skipped: ", counter)
        print("Exiting Adding Tor Nodes")
    return asn_objects
