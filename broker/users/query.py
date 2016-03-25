#!/usr/bin/env python

from pexpect import pxssh
import getpass
import os
import sys
import json
import subprocess


#BROKER_IP = "52.91.27.217"
CLIENT_PATH = "/project/shared/uiuc2015/broker/client.py"
BROKER_IP = "conduit"


cmd = CLIENT_PATH + " query " + BROKER_IP
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
out, err = p.communicate() 
res = out.split('\n')
print("Content-type: application/json\n\n")
for r in res:
    if not r.startswith('#'):
        print(r)


