import pymongo
import pandas as pd
from cfg import *

client = pymongo.MongoClient(MONGO_URL)
db = client[DATABASE]
col = db[COLLECTION]
cursor = col.find()
records = []

print "Loading records from mongo %s %s" % (DATABASE,COLLECTION)
try:
	for i,rec in enumerate(cursor):
		print i,
		records.append(rec)
except KeyboardInterrupt:
	print 
	print "User interrupt"
		

df = pd.DataFrame(records)
fname = COLLECTION + ".csv"
df.to_csv(fname, encoding='utf8')
print "Saved records to", fname
