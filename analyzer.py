import math
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from pymongo import MongoClient
from cfg import *

params = ['ppg', 'mpg', 'apg', 'topg', 'spg', 'bpg', 'rpg', 'orpg', 'drpg', 'fpg']
client = MongoClient(MONGO_URL)
db = client[DATABASE]
season = db[SEASON_COLLECTION]

labels = []
data = []
x_axis = []
y_axis = []

for p in season.find():
  stats = p['value']
  filtered_stats = {k : stats[k] for k in params } #filter the important params
  labels.append(p['_id']) # keep player names to use as labels for graph
  data.append(filtered_stats.values())

# reduce len(params) to n_components dimention
pca = PCA(n_components=2)
pca_data = pca.fit_transform(data)

# draw the results
for d in pca_data:
  x_axis.append(d[0])
  y_axis.append(d[1])

plt.scatter(x_axis, y_axis)
for label, x, y in zip(labels, x_axis, y_axis):
  plt.annotate(label, xy = (x, y))

plt.show()
