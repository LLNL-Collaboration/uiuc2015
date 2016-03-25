#! /usr/bin/env python

from subprocess import call
from pexpect import pxssh
import getpass
import sys
# server.py
import SocketServer
import time
from random import randint
import json
import urllib
import signal

# see https://docs.python.org/2/library/socketserver.html

# BROKER_IP = "52.91.27.217"
BROKER_IP = "localhost"
CONDUIT_IP = "conduit"
CONDUIT_PATH = "/project/shared/conduit/build-debug/tests/conduit_io/t_conduit_io_websocket"
BROKER_PATH = "/project/shared/uiuc2015/broker/broker.py"
LORENZ_PATH = "http://lorenz/lorenz/lora/lora.cgi/user/ME/conduit/save"


def sighandler():
    print ("oops")
    exit()

def verify(secret):
    try:
        s = pxssh.pxssh()
        hostname = BROKER_IP
        username = getpass.getuser()
        s.login (hostname, username)
        job_id = "job_" + str(port)
        s.sendline (BROKER_PATH + ' verify ' + job_id + ' ' + secret )  # run a command
        s.prompt()             # match the prompt
        valid = s.before.split("\n")[1].strip()
        s.logout()
        return valid
    except pxssh.ExceptionPxssh,e:
        print ("pxssh failed on login.")
        print (str(e))
        return false


def lorenz():
    url = LORENZ_PATH
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    job = data["output"]
    print (job)
    job = json.loads(job)

    cpath = job["cpath"]
    port = job["port"]
    print(cpath)
    print(port)
    print("\n")
    call([CONDUIT_PATH, "launch", "ssl", str(port), cpath])

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

    for i in [x for x in dir(signal) if x.startswith("SIG")]:
        try:
            signum = getattr(signal,i)
            signal.signal(signum,sighandler)
        except RuntimeError,m:
            print "Skipping %s"%i
        except ValueError,e:
            print ""

    # generate random port for the service to run on
    host = "localhost"
    if len(sys.argv)!=2:
        print("Usage: server.py ssl/ssh")
        exit()
    if sys.argv[1] in ['ssl','ssh']:
        ssl = sys.argv[1]
    elif "lorenz" in sys.argv:
        lorenz()
        exit()
    else:
        print("Usage: server.py ssl/ssh") 
        exit()

    #get secret from broker
    try:
        s = pxssh.pxssh()
        hostname = BROKER_IP
        username = getpass.getuser()
        s.login (hostname, username)
        s.sendline (BROKER_PATH + ' save '+ ssl)  # run a command

        s.prompt()             # match the prompt
        info = s.before.split("\n")[1].strip()

        print (info)
        info = json.loads(info)
        print (info)         # print everything before the prompt.
        port = info[0]
        s.logout()
    except pxssh.ExceptionPxssh,e:
        print "pxssh failed on login."
        print str(e)

    if ssl=="ssh":
        # Create the server, binding to localhost on selected port
        server = SocketServer.TCPServer((host, port), MyTCPHandler)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
    else:
        port = info[0]
        path = str(info[1])
        print(path)
        print(port)
        print("\n")
        call([CONDUIT_PATH, "launch", "ssl", str(port), path])
        print ("path:" + info[1])
        print (info[1])



