#! /usr/bin/env python

from pexpect import pxssh
import getpass

# server.py
import SocketServer
import time
from random import randint


# see https://docs.python.org/2/library/socketserver.html

BROKER_IP = "52.91.27.217"

def verify(secret):
    try:
        s = pxssh.pxssh()
        hostname = BROKER_IP
        username = getpass.getuser()
        s.login (hostname, username)
        s.sendline ('/project/shared/uiuc2015/broker/broker.py verify ' + secret)  # run a command
        s.prompt()             # match the prompt
        valid = s.before.split("\n")[1].strip()
        s.logout()
        return valid
    except pxssh.ExceptionPxssh,e:
        print "pxssh failed on login."
        print str(e)
        return false

class MyTCPHandler(SocketServer.BaseRequestHandler):

    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        valid = verify(self.data) == "True"
        ret = ""
        valid = 
        # if bad secret or error, fail gracefully
        if valid:
            print("client gave good secret")
            ret = "\n Correct Secret: \n Job Data: \n job data\n"
            self.request.sendall(ret)

        # if good secret, return job data
       else:
            print("client gave bad secret")
            ret = "\n Authorization Error: \n Bad Secret\n"
            self.request.sendall(ret)




if __name__ == "__main__":

    # generate random port for the service to run on
    host = "localhost"
    port = randint(8000, 10000)
    print("**************")
    print(port)

    #get secret to broker
    try:
        s = pxssh.pxssh()
        hostname = BROKER_IP
        username = getpass.getuser()
        s.login (hostname, username)
        s.sendline ('/project/shared/uiuc2015/broker/broker.py save ' + str(port))  # run a command
        s.prompt()             # match the prompt
        secret_string = s.before.split("\n")[1].strip()
        print secret_string         # print everything before the prompt.
        s.logout()
    except pxssh.ExceptionPxssh,e:
        print "pxssh failed on login."
        print str(e)

    # Create the server, binding to localhost on selected port
    server = SocketServer.TCPServer((host, port), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
