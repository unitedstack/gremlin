#!/usr/bin/env python

from __future__ import print_function

import subprocess
import json
import argparse
import random
import socket

_is_rack = False

def get_map():
    cmd = ['ceph', 'osd', 'crush', 'tree', '--format', 'json']
    ceph_osd_crush_tree_json = subprocess.check_output(cmd)
    ceph_osd_crush_tree = json.loads(ceph_osd_crush_tree_json)

    osd_map = {}
    global _is_rack

    for top_item in ceph_osd_crush_tree:
        if top_item['type'] == 'root':
            for l2_item in top_item['items']:
                if l2_item['type'] == 'rack':
                    _is_rack = True
                    osd_map[l2_item['name']] = {}
                    for l3_item in l2_item['items']:
                        if l3_item['type'] == 'host':
                            osd_map[l2_item['name']][l3_item['name']] = []
                            for osd in l3_item['items']:
                                if osd['type'] == 'osd':
                                    osd_map[l2_item['name']][l3_item['name']].append(osd['id'])
                elif l2_item['type'] == 'host':
                    _is_rack = False
                    osd_map[l2_item['name']] = []
                    for l3_item in l2_item['items']:
                        if l3_item['type'] == 'osd':
                            osd_map[l2_item['name']].append(l3_item['id'])
    return osd_map

def get_random_osd(num, same_bucket=False):

    osd_map = get_map()
    random_bucket = []
    osd = []
    random_osd = []

    for bucket in osd_map:
        random_bucket.append(bucket)
    random.shuffle(random_bucket)

    if same_bucket:
        bucket = random_bucket[0]
        
        if _is_rack:
            for host in osd_map[bucket]:
                osd.extend(osd_map[bucket][host])
        else:
            osd = osd_map[bucket]

    else:
        for bucket in random_bucket:
          if _is_rack:
              for host in osd_map[bucket]:
                  osd.extend(osd_map[bucket][host])
          else:
              osd.extend(osd_map[bucket])

    random.shuffle(osd)
    random_osd = osd[:num]

    return random_osd

def osd_to_host_ip(osd_id):
    osd_map = get_map()
    
    if _is_rack:
        for rack, hosts in osd_map.items():
           for host in hosts:
               if osd_id in osd_map[rack][host]:
                   return socket.gethostbyname(host)
    else:
        for host, osds in osd_map.items():
            if osd_id in osd_map[host]:
                return socket.gethostbyname(host)

def dump_random_osd_json(num, filename, same_bucket):
    ip_osd_map = {}
    random_osd = get_random_osd(num, same_bucket=same_bucket)
    for osd in random_osd:
        osd_host_ip = osd_to_host_ip(osd)
        if str(osd_host_ip) not in ip_osd_map:
            ip_osd_map[str(osd_host_ip)] = []
        ip_osd_map[str(osd_host_ip)].append(osd)

    json_file = open(filename, 'w')
    json_file.write(json.dumps(ip_osd_map))
    json_file.close() 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--same-bucket', action='store_true')
    parser.add_argument('-n', '--osd-down-num', nargs=1, type=int, default=0)
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('--list-pretty', action='store_true')
    args = parser.parse_args()

    if args.same_bucket:
        same_bucket = True
    else:
        same_bucket = False

    if args.list:
        print(json.dumps(get_map()))
    elif args.list_pretty:
        print(json.dumps(get_map(), indent=2))

    if args.osd_down_num:
        dump_random_osd_json(int(args.osd_down_num[0]), '/tmp/random-osd.json', same_bucket)
