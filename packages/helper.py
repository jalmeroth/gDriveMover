#!/usr/bin/python
import os
import sys
import json
import time
from email.utils import parseaddr


def updateStatus(status, finish, msg = None, bar_length = 10):
	"""docstring for updateStatus"""
	# do the math
	percent = float(status) / finish
	hashes = '#' * int(round(percent * bar_length))
	message = " [{0:10}] {1}/{2}".format(hashes, str(status), str(finish))
	
	# add some additional text
	if msg:
		message += ' '+ str(msg)
	
	# print out
	sys.stdout.write(message + '\r')
	sys.stdout.flush()

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

def main():
	"""docstring for main"""
	c = 10
	for i in range(c):
		time.sleep(1)
		updateStatus(i, c, "token"+str(i))

if __name__ == '__main__':
	main()