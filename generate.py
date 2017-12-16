#!/usr/bin/env python
import json
import requests
import cfscrape
import time

AFH_API_ENDPOINT = "https://androidfilehost.com/api/"
MAX_RETRIES = 5

page_count = 0
errors = ""
_f=open('devices.json','w')
list_devices=[]

def count_pages():
    global page_count
    global errors
    retries = 0
    scraper = cfscrape.create_scraper()
    payload={'action':'devices','limit':'1'}
    while True:
        data = []
        r = scraper.get(AFH_API_ENDPOINT, params=payload)
        try:
            data = r.json()
        except ValueError:
            if retries < MAX_RETRIES:
                retries += 1
                print r.content
                print "Error fetching number of pages. Retrying after 5s."
                time.sleep(5)
                continue
            else:
                errors += "\nError: could not fetch number of pages"
                break
        temp_page_count = 0
        try:
            temp_page_count = int(data['TOTALS']['total_objects'])
        except KeyError:
            errors += "\nError: unexpected JSON in count_pages()"
            break
        page_count = (temp_page_count/100) + 1
        break

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
        time.sleep(3)
    return devs


def get_devices():
    scraper = cfscrape.create_scraper()
    retries = 0
    global errors
    i = 1
    while i <= page_count:
      print "pass {0} of {1}".format(str(i),str(page_count))
      payload={'action':'devices','limit':'100','page':i}
      r = scraper.get(AFH_API_ENDPOINT, params=payload)
      rJson = []
      try:
          rJson = r.json()['DATA']
      except ValueError:
          if retries < MAX_RETRIES:
              retries += 1
              msg = "Error on page "
              msg += str(i)
              print r.content
              print msg
              time.sleep(5)
              # Retrying. So far, this has been a HTTP 502, and a retry fixes it
              # TODO: Check if it really is a 502
              continue
          else:
              errors += "\nError: could not fetch page "
              errors += str(i)
              retries = 0
              i += 1
              continue
      except KeyError:
          errors += "\nError: invalid JSON on page "
          errors += str(i)
          retries = 0
          i += 1
          continue
      list_devices.extend(rJson)
      print "Currently synced down {0} devices!".format(str(len(list_devices)))
      retries = 0
      i += 1
    json.dump(list_devices,_f,indent=2)

def get_developers():
    for i in list_devices:
        devs = fetch_devs(i['did'])
        _f = open(i['device_name'], 'w')
        json.dump(devs,_f,indent=2)

count_pages()
if page_count >= 1:
    get_devices()
    get_developers()
print errors
