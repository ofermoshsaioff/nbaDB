import sys
import requests
import time
import json
import datetime
from pymongo import MongoClient

URL_PREFIX = 'https://erikberg.com/'
APP_KEY = '98766e2d-0f0a-4257-84b1-3b70bf9894a5'
HEADERS = {'Authorization':'Bearer ' + APP_KEY, 'User-Agent': 'nbaDB 1.0 (ofer.moshaioff@gmail.com)'}

DATE_FORMAT = '%Y%m%d'
MOCK_DB = False

# DB init
if MOCK_DB:
	import mockdb
	games = mockdb.MockDb()
else:
	client = MongoClient('localhost', 27017)
	db = client['nbadb']
	games = db['games']

def insert_doc(doc, event_id):
    name = json.dumps(doc['display_name'])
    doc['id'] = event_id + '_' + name # adding a unique identifer: a concat of the event_id and the player's name, for example: 20131029-orlando-magic-at-indiana-pacers_Paul George
    print('Creating a record for', doc['id'])
    games.insert(doc)

def process_day(date):
	# step 1 - get all the events from the given date
	url = URL_PREFIX + 'events.json?date=' + date + '&sport=nba'
	print('Sending request to', url)
	req = requests.get(url, headers=HEADERS)
	res = req.json()

	# step 2 - for each event, get the box score and save it
	events = res['event']
	if len(events) == 0:
		print('No games on this day... sleeping 10 seconds and moving to the next day')

	time.sleep(10)

	for e in events:
		try:
			event_id = e['event_id']
			url = URL_PREFIX + 'nba/boxscore/' + event_id + '.json'
			print('Sending request to', url)

			req = requests.get(url, headers=HEADERS)
			bs = json.loads(req.text, 'utf-8')

			# step 3 - crop home/away stats and insert all the documents to the DB
			away = bs['away_stats']
			home = bs['home_stats']

		  	for h,a in zip(home, away):
				try:
					insert_doc(h, event_id)
					insert_doc(a, event_id)
				except Exception as err:
						print("Error inserting record to DB:", str(err))
						continue
		except:
		  	print('Error getting boxscore details for event', str(e))
		  	continue
		finally:
		  	print('Sleeping for 10 seconds...')
		  	time.sleep(10) # max 6 calls per minute allowed

# get a year from the user in YYYY format. TODO - add error handling
year = int(sys.argv[1])

# from http://www.daniweb.com/software-development/python/threads/45713/loop-through-a-year

# create date objects
begin_year = datetime.date(year, 10, 1)
end_year = datetime.date(year + 1, 4, 30)
one_day = datetime.timedelta(days=1)

next_day = begin_year
for day in range(0, 366):  # includes potential leap year
    if next_day > end_year:
        break
    try:
      	day_str = next_day.strftime(DATE_FORMAT)
      	print('Loading data for day', day_str)
      	process_day(day_str)
    except KeyboardInterrupt:
    	print('User interrupt')
    	break
    except:
      	print('Error processing day', day_str)
      	continue
    finally:
      	# increment date object by one day
      	next_day += one_day

if MOCK_DB:
	import cPickle as pickle
	with open("games.pickle", "wb") as fout:
		pickle.dump(games.data, fout)
	print("Mock DB written to file")