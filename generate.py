#!/usr/bin/env python
import json
import cfscrape
import time
import os

AFH_API_ENDPOINT = "https://androidfilehost.com/api/"
MAX_RETRIES = 5

page_count = 0
errors = ""
if not os.path.exists('./devices/'):
    os.makedirs('./devices/')
_f=open('./devices/devices.json','w')
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
    retries = 0
    payload={'action':'developers','page':'1','limit':'1','did':did}
    while True:
        raw = scraper.get(AFH_API_ENDPOINT, params=payload)
        objects = 0
        try:
            objects = int(raw.json()['TOTALS']['total_objects'])
        except ValueError:
            if retries < MAX_RETRIES:
                retries += 1
                msg = "Error fetching number of pages of developers for device "
                msg += str(did)
                print raw.content
                print msg
                time.sleep(5)
                # Retrying. So far, this has been a HTTP 502, and a retry fixes it
                # TODO: Check if it really is a 502
                continue
            else:
                errors += "\nError: could not fetch number of pages of developers for device "
                errors += str(did)
                return devs
        except KeyError:
            errors += "\nError: invalid JSON on pages of developers for device "
            errors += str(did)
            return devs
        except TypeError:
            # No developers
            return devs
        break

    temp_dev_pages_count = (objects / 100) + 1
    retries = 0
    i = 1
    while i <= temp_dev_pages_count:
        print "pass {0} of {1}".format(str(i), str(temp_dev_pages_count))
        payload={'action':'developers','page':i,'limit':'100','did':did}
        data = []
        raw = scraper.get(AFH_API_ENDPOINT,params=payload)
        try:
            data = raw.json()['DATA']
        except ValueError:
            if retries < MAX_RETRIES:
                retries += 1
                print raw.content
                print "Error fetching page {0} of developers for device {1}".format(str(i), str(did))
                time.sleep(5)
                # Retrying. So far, this has been a HTTP 502, and a retry fixes it
                # TODO: Check if it really is a 502
                continue
            else:
                errors += "\nError: could not fetch page {0} of developers for device {1}".format(str(i), str(did))
                retries = 0
                i += 1
                continue
        except KeyError:
            errors += "\nError: invalid JSON on page {0} of developers for device {1}".format(str(i), str(did))
            retries = 0
            i += 1
            continue
        devs.extend(data)
        time.sleep(3)
        retries = 0
        i += 1
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
              print r.content
              print "Error fetching page {0} of devices".format(str(i))
              time.sleep(5)
              # Retrying. So far, this has been a HTTP 502, and a retry fixes it
              # TODO: Check if it really is a 502
              continue
          else:
              errors += "\nError: could not fetch page {0} of devices".format(str(i))
              retries = 0
              i += 1
              continue
      except KeyError:
          errors += "\nError: invalid JSON on page {0} of devices".format(str(i))
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
        # Skipping devices we know has a huge number of devs. Trying to avoid DoS-ing here.
        if i['did'] == "51" or i['did'] == "395":
            continue
        print "Fetching developers for device {0} {1}".format(i['manufacturer'], i['device_name'])
        devs = fetch_devs(i['did'])
        if not os.path.exists('./developers/'):
            os.makedirs('./developers/')
        _f = open('./developers/' +i['did'], 'w')
        json.dump(devs,_f,indent=2)

count_pages()
if page_count >= 1:
    get_devices()
    is_travis = 'TRAVIS' in os.environ
    if not is_travis:
        get_developers()
print errors
