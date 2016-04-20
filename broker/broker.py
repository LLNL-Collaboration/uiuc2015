#!/usr/bin/env python

import os
import random
import binascii
import json
import getpass
import optparse
from config import *
from helpers import is_json
import shlex
import subprocess
from ConfigParser import SafeConfigParser
from helpers import is_json

#get path of configuration file
# configuration file is in the script's directory
dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]

config_file_path = os.path.join(dir, 'config.ini')
config = SafeConfigParser()
config.read(config_file_path)
USER_DIR_BASE = config.get('broker','USER_DIR_BASE')
CERTGEN_PATH = config.get('broker', 'CERTGEN_PATH')
DEBUG = config.getboolean('general','DEBUG')
DEBUG_PORT = config.get('general','DEBUG_PORT')
USERNAME = getpass.getuser()
FILEPATH = os.path.abspath(USER_DIR_BASE + USERNAME)
FILENAME = os.path.abspath(FILEPATH + "/connections.txt")


def get_jobs(fo):
        jobs = fo.read().split("\n")
        parsed_jobs = []
        for job in jobs:
                if not (is_json(job)):
                        continue
                parsed_jobs.append(json.loads(job))
        return parsed_jobs

def write_jobs(fo, jobs):
        # this function is not currently used, but you may want to check it works properly if it is used in the future
        fo.seek(0)
        fo.truncate()
        fo.write(jobs)

#test this
def append_job(fo, job):
        fo.write(json.dumps(job))
        fo.write("\n")

def save_job(fo, ctype):
        port = get_fresh_port(fo)
        jobs = get_jobs(fo)
        # TODO
        # check if job is already in jobs
        # if it is, update the job, and rewrite file

        # else just append new job
        secret = binascii.hexlify(os.urandom(512))
        job_id = "job_" + str(port)
        job = {"job_id": job_id, "port": port, "secret": secret, "ctype": ctype}
        append_job(fo, job)
        key = ""
        if ctype == 'ssl':
                command = CERTGEN_PATH + " " + FILEPATH + "/" + job_id
                command = shlex.split(command)
                subprocess.Popen(command)
                key = FILEPATH+"/" + job_id + ".pem"
        
        return { "port" : port , "cpath" : key }

def get_fresh_port(fo):
        if DEBUG:
                return DEBUG_PORT
        jobs = get_jobs(fo)
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
parser.add_option('-s', '--save', dest='save',
                  help='called when the server needs to register a job')
options, args = parser.parse_args()


with open(FILENAME, "a+") as pfile:
    if options.load:
        jobs = get_jobs(pfile)
        for job in jobs:
            if job.get("job_id") == options.load:
                print json.dumps(job)

    elif options.query:
        jobs = get_jobs(pfile)
        job_ids = []
        for job in jobs:
            job_ids.append((job["job_id"], job["port"]))
        print json.dumps(jobs)

    elif options.verify:
        job_id = options.verify[0]
        secret = options.verify[1]
        valid = False
        jobs = get_jobs(pfile)
        for job in jobs:
            if job['job_id'] == job_id:
                if job['secret'] == secret:
                    valid = True
        print valid

    elif options.save:
        if options.save.lower() not in ['ssl', 'ssh']:
            print "usage: save (ssh/ssl)"
        else:
            ret = save_job(pfile, options.save)
            print json.dumps(ret)
    else:
        print "invalid arg(s). Use 'load [job-id]', 'query', or 'save [ssh/ssl]'"
