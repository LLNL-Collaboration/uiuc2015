#!/usr/bin/env python3

import os
import random
import binascii
import json
import getpass
import optparse
import shlex
import subprocess
import configparser
from helpers import *
import importlib.util
import socket

#get path of configuration file
# configuration file is in the script's directory

current_dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(current_dir, 'config.ini')
config = configparser.SafeConfigParser()
config.read(config_file_path)
USER_DIR_BASE = config.get('broker','USER_DIR_BASE')
DEBUG = config.getboolean('general','DEBUG')
DEBUG_PORT = config.get('general','DEBUG_PORT')
APPLICATION_OPTIONS = config.get('general', 'APPLICATION_OPTIONS')
USERNAME = getpass.getuser()
FILEPATH = os.path.abspath(USER_DIR_BASE + USERNAME) + "/"
FILENAME = os.path.abspath(FILEPATH + "connections.txt")


def get_jobs(fo):
        jobs = fo.read().split("\n")
        parsed_jobs = []
        for job in jobs:
                if not (is_json(job)):
                        continue
                parsed_jobs.append(json.loads(job))
        return parsed_jobs

def append_job(FILENAME, job):
        with open(FILENAME, "a") as job_list:
            job_list.write(json.dumps(job))
            job_list.write("\n")

def save_job(jobs, app, password, ctype, app_module):
        port = get_fresh_port(jobs)
        job_id = "job_" + str(port)
        hostname = socket.gethostname()
        job = {"job_id": job_id, "port": port, "app" : app, "ctype": ctype, "password_hash" : password, "app_path" : config.get(app, 'SERVER_PATH'), "job_root" : FILEPATH, "host" : hostname, "owner" : USERNAME}

        #generate cert
        password_hash = password.split(":")[-1]
        app_module.gen_cert(job, password_hash)

        # gen config
        config_path = app_module.gen_config(job)
        job["config"] = config_path
        append_job(FILENAME, job)

        return job


def get_fresh_port(jobs):
        if DEBUG:
                return DEBUG_PORT
        current_ports = set()
        for job in jobs:
                current_ports.add(job["port"])
        new_port = random.randint(8000, 10000)
        while new_port  in current_ports:
            new_port = random.randint(8000, 10000)



parser = optparse.OptionParser()
parser.add_option('-l', '--load', dest='load', help='job_id to get information about')
parser.add_option('-q', '--query', action='store_true',
                  dest='query', help='returns job list in json')
parser.add_option('-v', '--verify', nargs=2, dest='verify',
                  help='verify the secret with a secret matching the job_id in connections.txt')
parser.add_option('-s', '--save', action='store_true', dest='save',
                  help='called when the server needs to register a job')
parser.add_option('-a', '--app', dest='app',
                  help='determines which application to run')
parser.add_option('-p', '--password', dest='password',
                  help='hash of the password to protect applciation')
options, args = parser.parse_args()


with open(FILENAME, "r+") as job_list:
    jobs = get_jobs(job_list)

if options.load:
    for job in jobs:
        if job.get("job_id") == options.load:
            print(json.dumps(job))

elif options.query:
    job_ids = []
    for job in jobs:
        job_ids.append((job["job_id"], job["port"]))
    print(json.dumps(jobs))

elif options.verify:
    job_id = options.verify[0]
    secret = options.verify[1]
    valid = False
    jobs = get_jobs(jobs)
    for job in jobs:
        if job['job_id'] == job_id:
            ## TODO ##
            # verify using app specific hash #
            if job['secret'] == secret:
                print("Not yet implemented")
                exit()
    print("Not yet implemented")
    exit()

elif options.save:
    if options.app:
        app = options.app.lower()
        if app not in APPLICATION_OPTIONS:
            parser.print_help()
            exit()
        if options.password:
            password = options.password
        else:
            password = None
        app_module = get_app_module(app)
        ret = save_job(jobs, app, password, "ssl", app_module);
        print(json.dumps(ret))
    else:
        parser.print_help()
        exit()
else:
    parser.print_help()

