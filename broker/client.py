#!/usr/bin/env python

from pexpect import pxssh
import getpass
import os

try:                                                            
	s = pxssh.pxssh()
	#connect to broker
        hostname = '52.91.27.217'
        username = getpass.getuser()
        s.login (hostname, username)
	#send command to execute broker to get the connection information	        
	s.sendline ('/project/shared/uiuc2015/broker/broker.py load')
        s.prompt()
	#get the port
        job = s.before.split("\n")[1].strip()
        job = job.split(":")
	port = job[0]
	secret = job[1]
	print("port is " + port)
	print("secret is " + secret)
	s.logout()
	#connect to the port
	server = "localhost"
	tunnel = "ssh -fnNT -L 6000:localhost:" + port + " " + username + "@" + server
	print(tunnel)
	os.system(tunnel)
	command = "curl localhost:6000"
	os.system(command)	
except pxssh.ExceptionPxssh,e:
        print "pxssh failed on login."
        print str(e)
