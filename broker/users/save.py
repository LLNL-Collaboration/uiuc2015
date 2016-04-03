#!/usr/bin/env python

import sys
import os
import random 
import binascii
import json
import getpass
from pexpect import pxssh

username = getpass.getuser()
filepath = os.path.abspath('/project/shared/home/' + username)
filename = os.path.abspath(filepath + "/connections.txt")
certgen_path = "/project/shared/uiuc2015/broker/certgen.sh"
BROKER_IP = "conduit"
CONDUIT_IP = "conduit"
BROKER_PATH = "/project/shared/uiuc2015/broker/broker.py"


def run(command, host):
    try:
        s = pxssh.pxssh()
        hostname = host
        username = getpass.getuser()
        s.login (hostname, username)
        s.sendline (command)
        s.prompt()
        output = s.before.split("\r\n")[1:-1]
        s.logout()
        return output
    except pxssh.ExceptionPxssh,e:
            print "pxssh failed on login."
            print str(e)


print "Content-type: application/json\n\n"
a = run(BROKER_PATH + " save ssl", CONDUIT_IP)[0]
print(json.dumps(a))