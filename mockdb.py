# -*- coding: utf-8 -*-
from datetime import datetime
from random import random
DATE_FORMAT = "%d/%m/%Y"

def datetime_from_string(string):
	return datetime.strptime(string, DATE_FORMAT)

class MockDb:
	def __init__(self):
		self.data = []


	def insert(self, post):
		_id = random()
		post['_id'] = _id
		self.data.append(post)
		return _id


	def find(self, spec=None, sort=None):
		if spec:
			data = []
			for d in self.data:
				match = True
				for k,v in spec.items():
					if d[k] != v:
						match = False
						break
				if match:
					data.append(d)
			return data
		else:
			return self


	def find_one(self, spec=None, sort=None):
		data = self.find(spec, sort)
		if len(data) > 0:
			return data[0]
		else:
			return None


	def rewind(self):
		return self


	def __iter__(self):
		return self.data.__iter__()


	def count(self):
		return len(self.data)


	def remove(self, _id):
		for x in self.data:
			if x['_id'] == _id:
				return self.data.remove(x)
