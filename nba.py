import sys
import requests
import time
import json
import datetime
from pymongo import MongoClient
from cfg import *

HEADERS = {'Authorization':'Bearer ' + APP_KEY, 'User-Agent': USER_AGENT}

# DB init
if MOCK_DB:
	import mockdb
	games = mockdb.MockDb()
else:
	client = MongoClient(MONGO_URL)
	db = client[DATABASE]
	games = db[COLLECTION]

def insert_doc(doc, general_stats):
	for k in general_stats:
		doc[k] = general_stats[k]
	print('Creating a record for %s for game %s' % (doc['display_name'], doc['event_id']))
	games.insert(doc)

def process_day(date):
	# step 1 - get all the events from the given date
	url = XML_STATS_URL + 'events.json?date=' + date + '&sport=nba'
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
			url = XML_STATS_URL + 'nba/boxscore/' + event_id + '.json'
			print('Sending request to', url)

			req = requests.get(url, headers=HEADERS)
			bs = json.loads(req.text, 'utf-8')

			# get general stats to store with each record
			general_stats = {}
			general_stats['event_id'] = event_id
			general_stats['type'] = bs['event_information']['season_type']
			general_stats['date'] = bs['event_information']['start_date_time']
			general_stats['home_team'] = bs['home_team']['team_id']
			general_stats['away_team'] = bs['away_team']['team_id']

			# step 3 - crop home/away stats and insert all the documents to the DB
			away = bs['away_stats']
			home = bs['home_stats']

			for h,a in zip(home, away):
				try:
					insert_doc(h, general_stats)
					insert_doc(a, general_stats)
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
	fname = COLLECTION + ".pickle"
	with open(fname, "wb") as fout:
		pickle.dump(games.data, fout)
	print("Mock DB written to file", fname)
