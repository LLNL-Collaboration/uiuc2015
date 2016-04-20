#! /usr/bin/env python

import getpass
import os
import atexit
import SocketServer
import json
import urllib
import signal
import optparse
import time
from time import sleep
from random import randint
from subprocess import call
from subprocess import Popen
from pexpect import pxssh
from config import *
from helpers import run


def kill_child():
    if child_pid is None:
        pass
    else:
        os.kill(child_pid, signal.SIGTERM)

def verify(secret):
    host = BROKER_IP
    command = BROKER_PATH + ' verify ' + job_id + ' ' + secret
    res = run(command, host)
    return res

def lorenz():
    url = LORENZ_PATH
    if LOCAL:
        print "local"
        cmd = BROKER_PATH + " save ssl"
        data = run(cmd, BROKER_IP)
        job = json.loads(data[0])
    else:
        response = urllib.urlopen(url)
        print response
        data = json.loads(response.read())
        job = data["output"]
        job = json.loads(job)

    cpath = job["cpath"]
    port = job["port"]
    print cpath, port
    print [SERVER_PATH, "launch", "ssl"]
    proc = Popen([SERVER_PATH, "launch", "ssl"])
    print SERVER_PATH
    child_pid = proc.pid
    (output, error) = proc.communicate()
    #proc.wait()
    if error:
        print "error:", error

    print "output:", output

if __name__ == "__main__":
    # don't leave orphan application running
    child_pid = None
    atexit.register(kill_child)


    # generate random port for the service to run on

    host = "localhost"
    parser = optparse.OptionParser()
    parser.add_option('-s', '--save', dest='save',
                      help='run broker with save parameter')
    parser.add_option('-l', '--lorenz', action='store_true', dest='lorenz')
    options, args = parser.parse_args()

    if options.save:
        if options.save in ['ssl', 'ssh']:
            ssl = options.save

    elif options.lorenz:
        lorenz()
        exit()

    else:
        print "Usage: server.py ssl/ssh"
        exit()

    #get secret from broker
    try:
        s = pxssh.pxssh()
        hostname = BROKER_IP
        username = getpass.getuser()
        s.login(hostname, username)
        s.sendline(BROKER_PATH + ' save '+ ssl)  # run a command

        s.prompt()             # match the prompt
        info = s.before.split("\n")[1].strip()

        print info
        info = json.loads(info)
        print info         # print everything before the prompt.
        port = info[0]
        s.logout()
    except pxssh.ExceptionPxssh, e:
        print "pxssh failed on login."
        print str(e)

    if ssl == "ssh":
        # Create the server, binding to localhost on selected port
        server = SocketServer.TCPServer((host, port), MyTCPHandler)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
    else:
        port = info[0]
        path = str(info[1])
        print path
        print port
        print "\n"
        call([SERVER_PATH, "launch", "ssl", str(port), path])
        print "path:" + info[1]
        print info[1]
