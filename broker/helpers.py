
from pexpect import pxssh
import getpass
import os
import sys
import json



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

def is_json(myjson):
        try:
                json_object = json.loads(myjson)
        except ValueError, e:
                return False
        return True