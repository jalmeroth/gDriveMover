#!/usr/bin/python
import os
import json
from email.utils import parseaddr

def validEmail(email):
	addr = parseaddr(email)
	return True if addr[1] != '' else False

def work_dir(path = '../'):
	"""docstring for _work_dir"""
	return os.path.dirname(os.path.realpath(os.path.join(__file__, path)))

def save(data, filename):
	"""docstring for save"""
	file = os.path.join(work_dir(), filename)
	with open(file, "w+") as jsonFile:
		json.dump(data, jsonFile)
	
def load(filename):
	"""docstring for load"""
	file = os.path.join(work_dir(), filename)
	
	if os.path.exists(file):
		with open(file,"r") as jsonFile:
			return json.load(jsonFile)
	else:
		return {}
