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
	s.sendline ('/project/shared/broker.py load')
        s.prompt()
	#get the port
        port = s.before.split("\n")[1].strip()
        s.logout()
	#connect to the port
	command = "curl localhost:" + str(port)
	os.system(command)	
except pxssh.ExceptionPxssh,e:
        print "pxssh failed on login."
        print str(e)
