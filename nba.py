import sys
import requests
import time
import json
from pymongo import MongoClient

URL_PREFIX = 'https://erikberg.com/'
APP_KEY = '98766e2d-0f0a-4257-84b1-3b70bf9894a5'
HEADERS = {'Authorization':'Bearer ' + APP_KEY}

# DB init
client = MongoClient('localhost', 27017)
db = client['nbadb']
players = db['players']

#get a YYYYMMDD date format from the user. TODO - if no input recieved, need to exit gracefully
date = sys.argv[1]

def handle_box_score(bs):

  away = bs['away_stats']
  home = bs['home_stats']

  for h,a in zip(home, away):
    print('inserting ' + json.dumps(h['display_name']) + ' to db')
    print('inserting ' + json.dumps(a['display_name']) + ' to db')

    players.insert(h)
    players.insert(a)

# step 1 - get all the events from the given date
url = URL_PREFIX + 'events.json?date=' +date + '&sport=nba'
print('sending request to: ' + url)
r = requests.get(url, headers=HEADERS)
d = r.json()

# step 2 - for each event, get the box score and save it
events = d['event']
for e in events:

  event_id = e['event_id'] #the unique id of the event
  url = URL_PREFIX + 'nba/boxscore/' + event_id + '.json'
  print('sending request to: ' + url)

  r = requests.get(url, headers=HEADERS)
  bs = json.loads(r.text, 'utf-8')
  handle_box_score(bs)

  print('sleeping for 10 seconds...')
  time.sleep(10) # max 6 calls per minute allowed




