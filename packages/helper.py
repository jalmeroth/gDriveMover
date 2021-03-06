#!/usr/bin/python
import os
import sys
import json
import time
from email.utils import parseaddr


def output(message):
    sys.stdout.write('\r' + message + '\033[K')
    sys.stdout.flush()
    return ''

def updateStatus(status = 0, finish = 0, before = None, after = None, bar_length = 10):
    """docstring for updateStatus"""
    
    message = ''
    
    # add some additional text
    if before:
        message += ' '+ str(before) if message else str(before)

    if status >= 0 and finish > 0:
    # do the math
        percent = float(status) / finish
        hashes = '#' * int(round(percent * bar_length))
        message = "[{0:10}] {1}/{2}".format(hashes, str(status), str(finish))
    
    # add some additional text
    if after:
        message += ' '+ str(after) if message else str(after)
    
    return output(message)

def validEmail(email):
    addr = parseaddr(email)
    return True if addr[1] != '' else False

def work_dir(path = '../'):
    """docstring for _work_dir"""
    return os.path.dirname(os.path.realpath(os.path.join(__file__, path)))

def unlink(filename):
    file = os.path.join(work_dir(), filename)
    try:
        os.remove(file)
    except OSError:
        pass

def save(data, filename):
    """docstring for save"""
    file = os.path.join(work_dir(), filename)
    
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))
    
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
        
    print output('lala')
    print output('lala')

if __name__ == '__main__':
    main()