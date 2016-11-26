#!/usr/bin/env python
import json
import requests

AFH_API_ENDPOINT = "https://androidfilehost.com/api/"
PAGE_COUNT = 0 # we'll calculate this below, chill

def dump_devices(d,f):
  json.dump(f,d,indent=2)

_f=open('devices.json','w')
list_devices=[]

def count_pages():
    payload={'action':'devices','limit':'1'}
    data = requests.get(AFH_API_ENDPOINT, params=payload).json()
    temp_page_count = int(data['TOTALS']['total_objects'])
    global PAGE_COUNT
    PAGE_COUNT = (temp_page_count/100) + 1

def get_devices():
    i = 1
    while i <= PAGE_COUNT:
      print "pass {0} of {1}".format(str(i),str(PAGE_COUNT))
      payload={'action':'devices','limit':'100','page':i}
      r = requests.get(AFH_API_ENDPOINT, params=payload)
      list_devices.extend(r.json()['DATA'])
      print "Currently synced down {0} devices!".format(str(len(list_devices)))
      i+=1
    json.dump(list_devices,_f,indent=2)

count_pages()
get_devices()
