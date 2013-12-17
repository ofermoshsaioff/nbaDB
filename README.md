nbaDB
=====

for now, a simple python script for d/l nba data to a local mongoDB instance.
all data is taken from Erik Berg's [xmlstats](https://erikberg.com/api)

Installation
============

all you need is:

- Love
- Python 3.3
- MongoDB (a running instance, to install mongo as a service, click [here](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-windows/#mongodb-as-a-windows-service))

Usage
=====

run `nba.py` with a specific date in `YYYYMMDD` format to insert data from all the games on that date. for example:
`python nba.py 20131216` will retrieve and insert all the data from 16-12-2013.

Goal
====

- Get Ofer to another NBA game
- Hopefully Yoav too
- Grantland, here we come!






