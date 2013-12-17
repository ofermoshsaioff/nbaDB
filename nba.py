import sys
import requests
import time
import json
from pymongo import MongoClient

URL_PREFIX = 'https://erikberg.com/'
APP_KEY = '98766e2d-0f0a-4257-84b1-3b70bf9894a5'
HEADERS = {'Authorization':'Bearer ' + APP_KEY}

client = MongoClient('localhost', 27017)
db = client['nbadb']
players = db['players']

date = sys.argv[1] #get a YYYYMMDD date format from the user

def str_to_unicode(str):
  return str.encode('utf-8').decode('utf-8')

def parse_box_score(bs):

  away = bs['away_stats']
  home = bs['home_stats']

  for h,a in zip(home, away):
    print('inserting ' + str_to_unicode(h['display_name']) + ' to db')
    print('inserting ' + str_to_unicode(a['display_name']) + ' to db')
    players.insert(h)
    players.insert(a)

url = URL_PREFIX + 'events.json?date=' +date + '&sport=nba'
print('sending request to: ' + url)
r = requests.get(url, headers=HEADERS)
d = r.json()

events = d['event']
for e in events:

  event_id = e['event_id'] #the unique id of the event
  url = URL_PREFIX + 'nba/boxscore/' + event_id + '.json'
  print('sending request to: ' + url)

  r = requests.get(url, headers=HEADERS)
  bs = json.loads(str_to_unicode(r.text))
  parse_box_score(bs)
  time.sleep(10) # max 6 calls per minute allowed



