#! /usr/bin/env python3

import getpass
import os
import atexit
import json
import urllib
import signal
import configparser
import os
import atexit
import optparse
import time
import getpass
import crypt
import hashlib
import importlib.util

from binascii import hexlify
from time import sleep
from random import randint
from subprocess import call
from subprocess import Popen
from pexpect import pxssh
from helpers import *

config = configparser.SafeConfigParser()
dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(dir, 'config.ini')
config.read(config_file_path)
BROKER_IP = config.get('general','BROKER_IP')
BROKER_PATH = config.get('general','BROKER_PATH')
LOCAL = config.getboolean('general', 'LOCAL')
LORENZ_PATH = config.get('general', 'LORENZ_PATH')
USER_DIR_BASE = config.get('broker','USER_DIR_BASE')
USERNAME = getpass.getuser()
FILEPATH = os.path.abspath(USER_DIR_BASE + USERNAME)

# def kill_child():
#     if child_pid is None:
#         os.kill(child_pid, signal.SIGKILL)
#         print("here")
#         pass
#     else:
#         print("not here")
#         os.kill(child_pid, signal.SIGKILL)
#         os.kill(child_pid, signal.SIGKILL)



def get_password_hash(app_module):
    return app_module.get_password()

def prep_run_command(app_module, job):
    cmd_str = app_module.get_launch_cmd(job)
    return cmd_str.split(" ")

def run_app(app):
    app_module = get_app_config(app)
    require_password = config.get(app,'REQUIRE_PASSWORD') == "True"
    print(require_password)
    if(require_password):
        password_hash = get_password_hash(app_module)
        pass_param = " -p " + password_hash
    else:
        pass_param = ""
    url = LORENZ_PATH
    if LOCAL:
        print("local")
        cmd = BROKER_PATH + " -s -a " + app + pass_param
        data = run(cmd, BROKER_IP)
        print(data)
        job = json.loads(data[0])
    else:
        response = urllib.urlopen(url)
        print(response)
        data = json.loads(response.read())
        job = data["output"]
        job = json.loads(job)

    print(job)
    cmd = prep_run_command(app_module, job)
    print(cmd)
    proc = Popen(cmd)
    child_pid = proc.pid
    print(child_pid)
    (output, error) = proc.communicate()
    ### tell broker the child pid ###
    #proc.wait()
    if error:
        print("error:", error)
    print("output:", output)



if __name__ == "__main__":
    # don't leave orphan application running
    child_pid = None

    # generate random port for the service to run on

    host = "localhost"
    parser = optparse.OptionParser()
    parser.add_option('-s', '--save', dest='save',
                      help='run broker with save parameter')
    parser.add_option('-a', '--app', dest='app',
                  help='Determines which application to run. Use either conduit or juypter')
    options, args = parser.parse_args()

    # if options.save:
    #     if options.save in ['ssl', 'ssh']:
    #         ssl = options.save

    print(options, args)
    if options.app:
        app = options.app.lower()
        print(app)

        if app not in ['conduit', 'jupyter']:
            print("please use conduit or jupyter for app")
            exit()
        run_app(app);

    else:
        print("Usage: server.py ssl/ssh app must be jupyter or conduit")
        exit()