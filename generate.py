#!/usr/bin/env python
import json
import requests

AFH_API_ENDPOINT = "https://androidfilehost.com/api/"
PAGE_COUNT = 9

def dump_devices(d,f):
  json.dump(f,d,indent=2)

#_f=open('devices.json','w')
list_devices=[]

def get_devices():
  i = 0
  while i <= 9:
    print "pass {0} of {1}".format(str(i),str(PAGE_COUNT))
    payload={'action':'devices','limit':'100','page':i}
    r = requests.get(AFH_API_ENDPOINT, params=payload)
    list_devices.extend(r.json()['DATA'])
    print "Currently synced down {0} devices!".format(str(len(list_devices)))
    i+=1

def recurse_devices_for_files():
  j = 0
  for i in list_devices:
    print "recursing for {0}".format(i["device_name"])
    payload={'action':'developers', 'did':i["did"]}
    r = requests.get(AFH_API_ENDPOINT, payload)
    print r.json()

list_devices=json.load(open('devices.json','r'))
recurse_devices_for_files()
