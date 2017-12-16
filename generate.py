#!/usr/bin/env python
import json
import requests
import cfscrape

AFH_API_ENDPOINT = "https://androidfilehost.com/api/"

_f=open('devices.json','w')
list_devices=[]

def count_pages():
    scraper = cfscrape.create_scraper()
    payload={'action':'devices','limit':'1'}
    data = scraper.get(AFH_API_ENDPOINT, params=payload).json()
    temp_page_count = int(data['TOTALS']['total_objects'])
    global PAGE_COUNT
    PAGE_COUNT = (temp_page_count/100) + 1

def fetch_devs(did):
    scraper = cfscrape.create_scraper()
    devs = []
    payload={'action':'developers','page':'1','limit':'1','did':did}
    data=scraper.get(AFH_API_ENDPOINT, params=payload).json()
    temp_dev_pages_count = (int(data['TOTALS']['total_objects'])/100) + 1
    while i <= temp_dev_pages_count:
        print "pass {0} of {1}".format(str(i),str(temp_dev_pages_count))
        payload={'action':'developers','page':i,'limit':'100','did':did}
        devs.extend(scraper.get(AFH_API_ENDPOINT,params=payload)).json()['DATA']
    return devs


def get_devices():
    scraper = cfscrape.create_scraper()
    i = 1
    while i <= PAGE_COUNT:
      print "pass {0} of {1}".format(str(i),str(PAGE_COUNT))
      payload={'action':'devices','limit':'100','page':i}
      r = scraper.get(AFH_API_ENDPOINT, params=payload)
      list_devices.extend(r.json()['DATA'])
      print "Currently synced down {0} devices!".format(str(len(list_devices)))
      i+=1
    json.dump(list_devices,_f,indent=2)

def get_developers():
    for i in list_devices:
        devs = fetch_devs(i['did'])
        _f = open(i['device_name'], 'w')
        json.dump(devs,_f,indent=2)

count_pages()
get_devices()
get_developers()
