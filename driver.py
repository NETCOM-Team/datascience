print("in driver.py")

import os
import time
import redis

import json
import csv
import os
import redis
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

import ipaddress
import re
import time

#creating lookups
import ipaddress
import pandas as pd

#geolite lookups
import ipaddress
import time
import pandas as pd


def main():
    """Driver function for ASN Program"""
    start_time = time.time()
    input_path = 'data/'
    output_path = 'master/'
    redis_instance = setup_redis()
    setup_directories(input_path, output_path)
    creating_files(input_path, output_path)
    creating_asns(output_path, input_path)
    stop_redis(redis_instance)
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
        create_geolite_lookup(input_path, output_path)
    if not os.path.exists(input_path + 'geolite_ordered.csv'):
        cleaning_geolite(input_path)


""" Starts a redis instance and checks whether or not this is a rolling ingest.
    If it is; it will increment the master version that should be outputted (1..n)
Returns
-------
    redis_instance (redis.StrictRedis): the connection to the redis database
"""
def setup_redis() -> redis.StrictRedis:
    redis_instance = start_redis()
    if os.path.exists('master/serialized_before'):
        redis_instance.incr('master_version')
    else:
        redis_instance.set('master_version', 1)
    return redis_instance

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
                      katz_centrality: float, score: float,
                      total_ips: int) -> object:

        """sets the attributes of an ASN object"""
        asn_obj.badness = badness
        asn_obj.ev_centrality = ev_centrality
        asn_obj.events_list = events_list
        asn_obj.tor_list = tor_list
        asn_obj.has_events = has_events
        asn_obj.katz_centrality = katz_centrality
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
        asn_objects[as_number].events_list.append(temp_event)
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

            temp_obj = ASN(int(key.decode('utf-8')))
            temp_obj = ASN.set_asn_attrs(temp_obj, asn_obj_dict['badness'], asn_obj_dict['ev_centrality'], asn_obj_dict['events_list'],
                                    asn_obj_dict['has_events'], asn_obj_dict['katz_centrality'], asn_obj_dict['score'],
                                    asn_obj_dict['total_ips'])
            asn_objs.append(temp_obj)
        except KeyError:
            pass
        except ValueError:
            pass
        except redis.exceptions.ResponseError:
            pass
        except AttributeError:
            pass

    print('done deserializing')
    asn_objs = sorted(asn_objs, key=lambda x: x.as_number)
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
    #redis_host = os.getenv('REDIS_HOST')
    redis_instance = redis.StrictRedis(host='redis', port=6379)
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
    files = get_files(input_path, 'Tor')
    """ create master df, resolve ASN's, rearrange df,
        and output to MASTER(1..n).csv
    """
    if files:
        tor_df = create_master_df(input_path,
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


"""
@author jacksonbrietzke
@author rajsingh
"""

""" This file contains functions which take in all of the Deepsight data, aggregate it, rename the columns, and output the
    processed data to a new, cleaner file called MASTER.csv. It will create 1-n versions of master (MASTER1, MASTER2, ..., MASTERn)
    based on how many consecutive data sets have been ingested.

"""



""" Aggregates the Deepsight data and outputs the new MASTER.csv (or MASTER2, MASTER3, ... , MASTERn.csv)
    based on how many times this program has been run (n) as part of the rolling ingestion process.

Args
-----
    input_path (str): The input path of the Deepsight files to aggregate
    output_path (str): The output path which signifies where the aggregated MASTER.csv will be placed

"""
def creating_files(input_path: str, output_path: str):
    """Creating Files."""
    print("Creating Files")
    master_output = '/MASTER.csv'
    """ Check whether or not this is part of the rolling ingest and not the initial run of the program
        If it is, change the name of the master version which is being output"""
    redis_instance = start_redis()
    if redis_instance.exists('master_version'):
        print('inside creating_files;')
        master_version = int(redis_instance.get('master_version').decode('utf-8'))
        print('master version: {}'.format(master_version))
        print('master version type: {}'.format(type(master_version)))
        if master_version > 1:
            print('master version bigger than 1?: {}'.format(master_version))
            master_output = '/MASTER' + str(master_version) + '.csv'
            stop_redis(redis_instance)
    else:
        stop_redis(redis_instance)

    file_name = "Deepsight"
    files = []
    col_names_dict = {}
    c_size = 1000

    """ open the data fields and names dict; data_fields.txt signifies
        the naming convention of the columns in the original files and
        names_dict.txt will be what they will be renamed to (so that
        they are easier to understand and work with"""
    with open(input_path + 'deepsight_fields.txt') as file:
        data_fields = file.read().splitlines()
    with open(input_path + 'deepsight_dict.txt') as file:
        for line in file:
            (key, value) = line.split(':')
            col_names_dict[str(key)] = value.rstrip()
    files = get_files(input_path, file_name)
    """ create master df, resolve ASN's, rearrange df,
        and output to MASTER(1..n).csv
    """
    master_df = create_master_df(input_path,
                                 files, c_size,
                                 data_fields)
    master_df.rename(columns=col_names_dict, inplace=True)
    master_df.to_csv(output_path + master_output)
    master_df = pd.read_csv(output_path + master_output,
                            low_memory=False)
    master_df = dropping_multiple_ips_asns(input_path, master_df)
    master_df.to_csv(output_path + master_output)

""" This function collects the Deepsight files and returns a list of all of them
    with newly named and parsed columns.

Args
-------
    input_path (str): The directory containing the Deepsight files to aggregate
    file_name (str): path to file to rename

Returns
-------
    file_list (list): The new list of files with cleaner columnn names
"""
def get_files(input_path: str, file_name: str) -> list:
    """Getting Files from directory using convention"""
    file_list = []
    for file in os.listdir(input_path):
        if file.startswith(file_name):
            """rename the columns into something sensible"""
            changing_line(file, input_path)
            file_list.append(file)
            print("Creating " + file)
    return file_list

"""This function alters the column names and makes them more readable.

Args
-------
    given_file (str): The filename whose columns should be renamed
    input_path (str): The path to 'given_file'

"""
def changing_line(given_file: str, input_path: str):
    """This function alters the column names"""
    with open(input_path + given_file, 'r') as file:
        lines = file.read().splitlines()
    lines[0] = lines[0].lower()
    """regular expressions to match column name patterns"""
    rep = {"domain.ipaddresses": "", "feed": "", "ipaddress": "",
           "ip.": "", "_": "", ".": "", "-": "", "xml": "", "domain": ""}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    lines[0] = pattern.sub(lambda m: rep[re.escape(m.group(0))], lines[0])
    with open(input_path + given_file, 'w')as file:
        file.write('\n'.join(lines))

""" This function creates the new, renamed MASTER dataframe by reading it in
    chunks at a time

Args
-------
    input_path (str): The path to the MASTER dataframe
    files (list): the list of files to condense into MASTER
    c_size (int): the size of the chunks
    data_fields (list): column names

Returns
-------
    df (pd.DataFrame): the finished MASTER dataframe with newly named columns
"""
def create_master_df(input_path: str, files: list,
                     c_size: int, data_fields: list) -> pd.DataFrame:
    """Creating DFs for both IP and URL Deepsight Data"""
    df = pd.DataFrame()
    for file in files:
        df_chunk = pd.DataFrame()
        for chunk in pd.read_csv(input_path + file, chunksize=c_size,
                                 usecols=lambda x: x in data_fields,
                                 encoding='utf-8'):
            df_chunk = pd.concat([df_chunk, chunk])

        df = pd.concat([df, df_chunk], sort=False)
    print('This is the length: ', len(df.index))
    return df

""" This function drops multiple IP / ASN entries. For example,
    if an event doesn't have an IP, it gets dropped. If the ASN is
    out of range, it gets dropped, etc. It returns a data frame with
    only valid, resolved ASNs (using resolve_asn) sorted by date and
    ASN number

Args
-------
    input_path (str): path to the geolite database to resolve ASN's
    df (pd.Dataframe): the MASTER data frame passed in containing Event/ASN info

Returns
-------
    df (pd.Dataframe): The dataframe with the updated ASN/Event info
"""
def dropping_multiple_ips_asns(input_path: str, df: pd.DataFrame) -> pd.DataFrame:
    """Getting rid of multiple IPs and ASNs"""
    print("Dropping multiple IPs and ASNs")
    drop_set = set()
    temp_list = []
    print('Looping through dataframe')
    counter = 0
    print("Length of DF: ", len(df.index))
    for x in range(len(df.index)):
        counter += 1
        ip_addr = str(df['IP_Address'][x])
        asn = str(df['ASN'][x])
        """drop unnecessary / invalid ASN's"""
        if ip_addr == 'nan':
            drop_set.add(x)
        elif ip_addr[0].isdigit() is False:
            drop_set.add(x)
        elif len(ip_addr) > 15:
#            This is commented out for Aaron's part
#            ip_list = df['IP_Address'][x].split(',')
#            for y in ip_list:
#                temp_rows = df.iloc[x].copy()
#                temp_rows['IP_Address'] = y
#                temp_rows['ASN'] = -1
#                temp_list.append(temp_rows)
            drop_set.add(x)
        elif asn == 'nan':
            drop_set.add(x)
        elif len(asn) > 12:
            drop_set.add(x)

    df.drop(drop_set, inplace=True)
    temp_df = pd.DataFrame(temp_list)
    temp_df.reset_index(drop=True, inplace=True)
    start_time = time.time()
    temp_df = resolve_asn(input_path, temp_df)
    print(time.time() - start_time)
    df = df.append(temp_df)
    df['ASN'] = pd.to_numeric(df['ASN'], downcast='integer')
    df.sort_values(by=['ASN', 'Source_Date'], inplace=True)
    return df

""" This function resolves an ASN and checks which IP addresses
    are associated with it. It maps each ASN to the multiple
    IP addresses that might be associated with it.

Args
-------
    input_path (str): path to the geolite database to resolve ASN's
    df (pd.Dataframe): the MASTER data frame passed in containing Event/ASN info

Returns
-------
    df (pd.Dataframe): The dataframe with the updated ASN/Event info
"""
def resolve_asn(input_path, df) -> pd.DataFrame:
    """Resolving the ASN when it is Zero"""
    print('Resolving ASN')
    geo_path = input_path + '/geolite_ordered.csv'
    geo_df = pd.read_csv(geo_path)
    df = sorting_by_address(df)
    print('Back to resolving')
    geo_counter = 0
    total_matches = 0
    """get valid IP's for each ASN"""
    for x in range(len(df.index)):
        match = False
        while(match is False and geo_counter < len(geo_df.index) -1):
            ip_sep = df.iloc[x]['IP_List']
            geo_ip_sep = geo_df.iloc[geo_counter]['IP_List'].strip('][').split(', ')
            is_ip_bigger = comparing_ip_size(ip_sep, geo_ip_sep)
            if is_ip_bigger:
                geo_counter += 1
            elif(ipaddress.ip_address(df.iloc[x]['IP_Address']) in
                 ipaddress.ip_network(geo_df.iloc[geo_counter]['IP_CIDR'])):
                df.at[x, 'ASN'] = geo_df.iloc[geo_counter]['ASN']
                match = True
                total_matches += 1
            else:
                match = True

    print('Total Matches: ', total_matches)
    df.drop(columns=['IP_List'], inplace=True)
    return df

"""Compares two IPv4 addresses

Args
-------
    ip1 (str): IP address 1
    ip2 (str): IP address 2

Returns
-------
    bool: True or false based on whether or not ip1 > ip2
"""
def comparing_ip_size(ip1, ip2) -> bool:
    """Checking the IP Size"""
#    print('Comparing IP Size', ip1, ip2)
    counter = 0
    while counter < 4:
        if int(ip1[counter]) < int(ip2[counter]):
            return False
        elif int(ip1[counter]) > int(ip2[counter]):
            return True
        counter += 1
    return False

"""sorts our Event/ASN dataframe by IP address

Args
-------
    df (pd.DataFrame): the dataframe to be sorted

Returns
-------
    df (pd.DataFrame): the dataframe sorted by IP address
"""
def sorting_by_address(df) -> pd.DataFrame:
    """Sorting By IP Address"""
    print('In Sorting By Address')
    ips = []
    for x in range(len(df.index)):
        ip_list = df.iloc[x]['IP_Address'].split('.')
        for y in range(0, 4):
            ip_list[y] = int(ip_list[y])
        ips.append(ip_list)
    df['IP_List'] = ips
    df.sort_values(by=['IP_List'], inplace=True)
    return df


"""
    This file looks up which IPs are in which ASN's and outputs them to geolite_lookup.csv
"""

""" driver function for creating the geolite lookup

Args
-------
    input_path (str): the path to the original Geolite database file
    output_path (str): the path to output the new Geolite look with less columns for our use

"""
def creating_ip_asn_lookups(input_path: str, output_path: str):
    """Creating ASN lookups for ASN Objs to use"""
    print("Creating IP/ASN Lookups")
    create_geolite_lookup(input_path, output_path)


""" Uses the Geolite database to lookup which IP's belong to which ASN's


Args
-------
    input_path (str): the path to the original Geolite database file
    output_path (str): the path to output the new Geolite look with less columns for our use

"""
def create_geolite_lookup(input_path: str , output_path: str):
    """Creating Geolite csv to find IP/ASN mapping"""
    print("Creating Geolite Lookup")
    max_asn = 600000
    geolite_input_file = input_path + 'geolite_original.csv'
    geolite_output_file = output_path + 'geolite_lookup.csv'
    geo_df = pd.read_csv(geolite_input_file)
    geo_df = geo_df.drop(geo_df.columns[[0, 1, 4]], axis=1)
    geo_df = geo_df[geo_df.ASN != '-']
    geo_df = geo_df.astype({'ASN': int})
    geo_df.sort_values(by='ASN', inplace=True)
    asn_list = []
    for number in range(0, max_asn):
        asn_list.append([number, 0])
    current_asn = 0
    current_ip_total = 0
    for index, row in geo_df.iterrows():
        if int(row['ASN']) == current_asn:
            current_ip_total += ipaddress.ip_network(row['IP_CIDR']).num_addresses
        else:
            asn_list[current_asn] = [current_asn, current_ip_total]
            current_asn = int(row['ASN'])
            current_ip_total = ipaddress.ip_network(row['IP_CIDR']).num_addresses
    asn_list[current_asn] = [current_asn, current_ip_total]
    df = pd.DataFrame(asn_list, columns=['ASN', 'Total_IPs'])
    df.to_csv(geolite_output_file)


""" Reads the geolite database and creates CIDR notation IP addresses for visualizations purposes

Args
-------
    input_path (str): the path to the geolite database
"""
def cleaning_geolite(input_path: str):
    """Main Function for creating CIDRs."""
    start_time = time.time()
    geo_input_path = input_path + 'geolite_original.csv'
    geo_df = pd.read_csv(geo_input_path)
    last_hosts_list = []
    drop_set = set()
    for number in range(len(geo_df.index)):
        if geo_df['ASN'][number] == '-':
            drop_set.add(number)
    geo_df.drop(drop_set, inplace=True)
    for index, row in geo_df.iterrows():
        network = ipaddress.ip_network(row['IP_CIDR'])
        last_hosts_list.append(network[-1])
    ips_separated = []
    for ip in last_hosts_list:
        temp_list = str(ip).split('.')
        for place in range(0, 4):
            temp_list[place] = int(temp_list[place])
        ips_separated.append(temp_list)
    geo_df['IP_List'] = ips_separated
    geo_df.sort_values(by=['IP_List'], inplace=True)
    geo_df.to_csv(input_path + 'geolite_ordered.csv')
    print("--- %s seconds ---" % (time.time() - start_time))





main()

