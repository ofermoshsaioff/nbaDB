import sys
import requests
import time
from pymongo import MongoClient

URL_PREFIX = 'https://erikberg.com/'
APP_KEY = '98766e2d-0f0a-4257-84b1-3b70bf9894a5'
HEADERS = {'Authorization':'Bearer ' + APP_KEY}

client = MongoClient('localhost', 27017)

date = sys.argv[1] #get a YYYYMMDD date format from the user

print('sending request to: ' + URL_PREFIX + 'events.json?date=' +date + '&sport=nba')
r = requests.get(URL_PREFIX + 'events.json?date=' + date + '&sport=nba', headers=HEADERS)
d = r.json()

events = d['event']
for e in events:
  id = e['event_id']
  print('sending request to: ' + URL_PREFIX + 'nba/boxscore/' + id + '.json')
  bs = requests.get(URL_PREFIX + 'nba/boxscore/' + id + '.json', headers=HEADERS)
  bs.encoding = 'utf-8'
  print(bs.json())
  time.sleep(10) # max 6 calls per minute allowed

