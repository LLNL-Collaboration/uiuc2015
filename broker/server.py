#! /usr/bin/env python

from pexpect import pxssh
import getpass

# server.py
import socket
import time
from random import randint

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
host = socket.gethostname()


port = randint(8000, 10000)
print("**************")
print(port)

#send secret to broker
try:
    s = pxssh.pxssh()
    hostname = '52.91.27.217'
    username = getpass.getuser()
    s.login (hostname, username)
    s.sendline ('/project/shared/broker.py save ' + str(port))  # run a command
    s.prompt()             # match the prompt
    print s.before         # print everything before the prompt.
    s.logout()
except pxssh.ExceptionPxssh,e:
    print "pxssh failed on login."
    print str(e)

# bind to the port
serversocket.bind(('', port))

# queue up to 5 requests
serversocket.listen(5)

while True:
    # establish a connection
    clientsocket,addr = serversocket.accept()
    
    print("Got a connection from %s" % str(addr))
    currentTime = time.ctime(time.time()) + "\r\n"
    clientsocket.send(currentTime.encode('ascii'))
    clientsocket.close()