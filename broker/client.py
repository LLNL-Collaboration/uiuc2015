#!/usr/bin/env python

from pexpect import pxssh
import getpass
import os

BROKER_IP = "52.91.27.217"

try:    
	###
	# get the secret from the broker
	###
                                                        
	s = pxssh.pxssh()
	#connect to broker
        hostname = BROKER_IP
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
	print("Broker says the port is: " + port)
	print("Broker says the secret is: " + secret)
	s.logout()

	###
	# get job data from server
	###

	#connect to the port
	server = "localhost"
	tunnel = "ssh -fnNT -L 6005:localhost:" + port + " " + username + "@" + server
	print("Opening a tunnel: \n" + tunnel)
	os.system(tunnel)
	command = 'echo "' + secret + '" | nc localhost 6005'
	print("Connecting to server with the secret: " + command)
	os.system(command)	
except pxssh.ExceptionPxssh,e:
        print "pxssh failed on login."
        print str(e)
