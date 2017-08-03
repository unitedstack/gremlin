#!/use/bin/env python

from __future__ import print_function

import subprocess
import json
import socket
import random
import time
import argparse

bucket_id_map = {}
host_osd_map = {}
osd_host_map = {}
pg_map = {}

def init_osd_map():

    CMD = ['ceph', 'osd', 'crush', 'dump', '--format', 'json']

    ceph_osd_crush_dump_json = subprocess.check_output(CMD)
    ceph_osd_crush_dump = json.loads(ceph_osd_crush_dump_json)
    
    global bucket_id_map
    for bucket in ceph_osd_crush_dump['buckets']:
        bucket_id_map[bucket['id']] = dict({'type': bucket['type_name'],
                                         'name': bucket['name'],
                                         'items': [ item['id'] for item in bucket['items']]})

    host_id_list = [ item for item in bucket_id_map.keys()
                     if bucket_id_map[item]['type'] == 'host']
    global host_osd_map
    for item in host_id_list:
        host_name = bucket_id_map[item]['name']
        host_ip = socket.gethostbyname(host_name)
        host_osds = bucket_id_map[item]['items']
        host_osd_map[host_name] = dict({'mgmt': host_ip,
                                        'id':  item,
                                        'osds': host_osds})

    global osd_host_map
    for host in host_osd_map.keys():
        for osd in host_osd_map[host]['osds']:
            osd_name = ceph_osd_crush_dump['devices'][osd]['name']
            osd_mgmt = host_osd_map[host]['mgmt']
            osd_host_map[osd] = dict({'host': host,
                                      'name': osd_name,
                                      'mgmt': osd_mgmt})

def init_pg_map():

    CMD = ['ceph', 'pg', 'dump', '--format', 'json']

    ceph_pg_dump_json = subprocess.check_output(CMD)
    ceph_pg_dump = json.loads(ceph_pg_dump_json)
   
    global pg_map
    for item in ceph_pg_dump['pg_stats']:
        pg_id = item['pgid']
        pg_map[pg_id] = item['acting']

def get_random_osd(map_data, num=1):

    random_osd = {}
    random_osd['size'] = num

    random.seed(time.time())
    random_osd_list = random.sample(map_data.keys(), num)
    random_osd['items'] = {}

    for osd in random_osd_list:
        random_osd['items'][osd] = map_data[osd]

    return random_osd  

def get_random_osd_from_pg(pg_map, osd_map):

    random_osd = {}

    random_pg_id = random.choice(pg_map.keys())
    random_osd['pgid'] = random_pg_id

    random_osd_list = pg_map[random_pg_id]
    random_osd['size'] = len(random_osd_list)
    random_osd['items'] = {}

    for osd in random_osd_list:
        random_osd['items'][osd] = osd_map[osd]

    return random_osd

def reformat_mgmt_osd_map(osd_map):

    mgmt_osd_map = {}

    for osd in osd_map:
        mgmt_addr = osd_map[osd]['mgmt']
        if mgmt_addr not in mgmt_osd_map.keys():
            mgmt_osd_map[mgmt_addr] = []
        mgmt_osd_map[mgmt_addr].append(osd)

    return mgmt_osd_map

def output_data(data, output_format='plain', filename=None):

    if filename:
        if output_format == 'plain':
            file_handler = open(filename, 'w')
            file_handler.write(data)  
        elif output_format == 'json':
            file_handler = open(filename + '.json', 'w')
            file_handler.write(json.dumps(data))
        elif output_format == 'json-pretty':
            file_handler = open(filename + '.json', 'w')
            file_handler.write(json.dumps(data, indent=2))
        else:
            print("Unsupport this {FORMAT} format".format(FORMAT=output_format))
        file_handler.close()
    else:
        if output_format == 'plain':
            print(data)
        elif output_format == 'json':
            print(json.dumps(data))
        elif output_format == 'json-pretty':
            print(json.dumps(data, indent=2))
        else:
            print("Unsupport this {FORMAT} format!".format(FORMAT=output_format))

def init_argument(parser):

    parser.add_argument('-n', '--number', nargs=1, type=int)
    parser.add_argument('-p', '--percentage', nargs=1, type=int)
    parser.add_argument('--list-host-map', action='store_true')
    parser.add_argument('--list-osd-map', action='store_true')
    parser.add_argument('--list-pg-map', action='store_true')
    parser.add_argument('-F', '--format', nargs=1)
    parser.add_argument('-f', '--file', nargs=1)
    parser.add_argument('--get-random-osd', action='store_true')
    parser.add_argument('--get-pg-osd', action='store_true')
    parser.add_argument('--mgmt-osd', action='store_true')

    args = parser.parse_args()

    return args

def take_action(args):

    if isinstance(args.format, list):
        output_format = args.format[0]
    else:
        output_format = 'plain'

    if isinstance(args.file, list):
        output_filename = args.file[0]
    else:
        output_filename = None

    if isinstance(args.percentage, list):
        percentage = args.percentage[0]
        osd_number = int(len(osd_host_map.keys()) * (percentage / 100.0))
    elif isinstance(args.number, list):
        osd_number = args.number[0]
    else:
        osd_number = 1

    if args.mgmt_osd:
        mgmt_osd_enabled = True
    else:
        mgmt_osd_enabled = False

    if args.list_host_map:
        output_data(host_osd_map, output_format, output_filename)

    if args.list_osd_map:
        if mgmt_osd_enabled:
            output_map = reformat_mgmt_osd_map(osd_host_map)
        else:
            output_map = osd_host_map
        output_data(output_map, output_format, output_filename)

    if args.list_pg_map:
        output_data(pg_map, output_format, output_filename)

    if args.get_random_osd:
        random_osd = get_random_osd(osd_host_map, osd_number)
        if mgmt_osd_enabled:
            output_map_temp = reformat_mgmt_osd_map(random_osd['items'])
            output_map = dict({'size': random_osd['size'],
                               'items': output_map_temp})
        else:
            output_map = random_osd
        output_data(output_map, output_format, output_filename)

    if args.get_pg_osd:
        random_osd = get_random_osd_from_pg(pg_map, osd_host_map)
        if mgmt_osd_enabled:
            osd_list = random_osd['items'].keys()
            output_list = []
            for num in range(1,random_osd['size'] + 1):
                random_osd_temp = {}
                for osd in osd_list[:num]:
                    random_osd_temp[osd] = random_osd['items'][osd]
                output_list.append(reformat_mgmt_osd_map(random_osd_temp))
            output_map = dict({'size': random_osd['size'],
                               'items': output_list})
        else:
            output_map = random_osd
        output_data(output_map, output_format, output_filename)
        
if __name__ == '__main__':

    init_osd_map()
    init_pg_map()

    parser = argparse.ArgumentParser()
    args = init_argument(parser)

    take_action(args)
