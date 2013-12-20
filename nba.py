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
	boxscores = db[BS_COLLECTION]
	teams = db[TEAMS_COLLECTION]

def get_date(datetime_str):
	date_str = datetime_str[:10]
	date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
	return date

def get_season(datetime_str):
	date = get_date(datetime_str)
	year = date.year
	month = date.month
	if 8 <= month <= 12:
		season = str(year) + '-' + str(year+1)
	else:
		season = str(year-1) + '-' + str(year)
	return season

def insert_bs(doc, general_stats):
	doc.update(general_stats)
	print 'Creating a player boxscore record for %s for game %s' % (repr(doc['display_name']), doc['event_id'])
	boxscores.insert(doc)

def insert_team(doc, general_stats, is_home):
	doc.update(general_stats)
	team_name = ''
	if is_home:
		team_name = doc['home_team']
	else:
		team_name = doc['away_team']
	doc['team_name'] = team_name
	print 'Creating a team record for %s for game %s' % (team_name, doc['event_id'])
	teams.insert(doc)

def process_day(date):
	# step 1 - get all the events from the given date
	url = XML_STATS_URL + 'events.json?date=' + date + '&sport=nba'
	print 'Sending request to %s' % url
	req = requests.get(url, headers=HEADERS)
	res = req.json()

	# step 2 - for each event, get the box score and save it
	events = res['event']
	if len(events) == 0:
		print 'No games on this day... sleeping 10 seconds and moving to the next day'

	time.sleep(10)

	for e in events:
		try:
			event_id = e['event_id']
			if e['event_status'] != 'completed' or (e['season_type'] != 'regular' and e['season_type'] != 'post'):
				print 'Game %s is either not played yet, or not a regular or playoff game, skipping it...' % event_id
				continue
			url = XML_STATS_URL + 'nba/boxscore/' + event_id + '.json'
			print 'Sending request to %s' % url

			req = requests.get(url, headers=HEADERS)
			bs = json.loads(req.text, 'utf-8')

			# get general stats to store with each record
			general_stats = {}
			general_stats['event_id'] = event_id
			general_stats['type'] = bs['event_information']['season_type']
			general_stats['date'] = get_date(bs['event_information']['start_date_time'])
			general_stats['season'] = get_season(bs['event_information']['start_date_time'])
			general_stats['home_team'] = bs['home_team']['team_id']
			general_stats['away_team'] = bs['away_team']['team_id']

			# step 3 - insert total team boxscore to teams collection
			home_totals = bs['home_totals']
			away_totals = bs['away_totals']
			insert_team(home_totals, general_stats, True)
			insert_team(away_totals, general_stats, False)

			# step 4 - crop home/away stats and insert all the documents to the boxscore table
			away = bs['away_stats']
			home = bs['home_stats']

			for h,a in zip(home, away):
				try:
					insert_bs(h, general_stats)
					insert_bs(a, general_stats)
				except Exception as err:
					print "Error inserting record to DB: %s" % str(err)
					continue
		except Exception as error:
			print 'Error getting boxscore details %s' % str(error)
			continue
		finally:
			print 'Sleeping for 10 seconds...'
			time.sleep(10) # max 6 calls per minute allowed

# get a year from the user in YYYY format. TODO - add error handling
year = int(sys.argv[1])

# from http://www.daniweb.com/software-development/python/threads/45713/loop-through-a-year

# create date objects
begin_year = datetime.date(year, 10, 15)
end_year = datetime.date(year + 1, 6, 30)
one_day = datetime.timedelta(days=1)

next_day = begin_year
for day in range(0, 366):  # includes potential leap year
	if next_day > end_year:
		break
	try:
		day_str = next_day.strftime(DATE_FORMAT)
		print 'Loading data for day %s' % day_str
		process_day(day_str)
	except KeyboardInterrupt:
		print 'User interrupt'
		break
	except:
		print 'Error processing day %s' % day_str
		continue
	finally:
		# increment date object by one day
		next_day += one_day

if MOCK_DB:
	import cPickle as pickle
	fname = COLLECTION + ".pickle"
	with open(fname, "wb") as fout:
		pickle.dump(games.data, fout)
	print "Mock DB written to file %s" % fname
