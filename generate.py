#!/usr/bin/env python
import json
import requests

AFH_API_ENDPOINT = "https://androidfilehost.com/api/"
PAGE_COUNT = 9

def dump_devices(d,f):
  json.dump(f,d,indent=2)

_f=open('devices.json','w')
list_devices=[]
i=1

while i <= 9:
  payload={'action':'devices','limit':'100','page':i}
  r = requests.get(AFH_API_ENDPOINT, params=payload)
  list_devices.extend(r.json()['DATA'])
  i+=1

json.dump(list_devices,_f,indent=2)
