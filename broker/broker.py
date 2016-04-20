#!/usr/bin/env python

import os
import random
import binascii
import json
import getpass
from config import *
from helpers import is_json
import optparse

username = getpass.getuser()
filepath = os.path.abspath(USER_DIR_BASE + username)
filename = os.path.abspath(filepath + "/connections.txt")

def get_jobs():
        if not os.path.isfile(filename):
                return []
        fo = open(filename, "r")
        jobs = fo.read().split("\n")
        parsed_jobs = []
        for job in jobs:
                if not (is_json(job)):
                        continue
                parsed_jobs.append(json.loads(job))
        return parsed_jobs

def write_jobs(jobs):
        fo = open(filename, "w")
        fo.write(jobs)

#test this
def append_job(job):
        with open(filename, "a") as fo:
                fo.write(json.dumps(job))
                fo.write("\n")

def save_job(ctype):
        port = get_fresh_port()
        jobs = get_jobs()
        # TODO
        # check if job is already in jobs
        # if it is, update the job, and rewrite file

        # else just append new job
        secret = binascii.hexlify(os.urandom(512))
        job_id = "job_" + str(port)
        job = {"job_id": job_id, "port": port, "secret": secret, "ctype": ctype}
        append_job(job)
        key = ""
        if ctype == 'ssl':
                command = CERTGEN_PATH + " " + filepath + "/" + job_id
                os.system(command)
                key = filepath+"/" + job_id + ".pem"

        return { "port" : port , "cpath" : key }

def get_fresh_port():
        if DEBUG:
                return DEBUG_PORT
        jobs = get_jobs()
        current_ports = set()
        for job in jobs:
                current_ports.add(job["port"])
        new_port = random.randint(8000, 10000)
        while new_port  in current_ports:
                new_port = random.randint(8000, 10000)
        return new_port

parser = optparse.OptionParser()
parser.add_option('-l', '--load', dest='load', help='job_id to get information about')
parser.add_option('-q', '--query', action='store_true', dest='query', help='returns job list in json')
parser.add_option('-v', '--verify', nargs=2, dest='verify', help='verify the secret with a secret matching the job_id in connections.txt')
parser.add_option('-s', '--save', dest='save', help='called when the server needs to register a job')
options, args = parser.parse_args()

if options.load:
    jobs = get_jobs()
    for job in jobs:
        if job.get("job_id") == options.load:
            print(json.dumps(job))

elif options.query:
    jobs = get_jobs()
    job_ids = []
    for job in jobs:
        job_ids.append((job["job_id"], job["port"]))
    print(json.dumps(jobs))

elif options.verify:
    job_id = options.verify[0]
    secret = options.verify[1]
    valid = False
    jobs = get_jobs()
    for job in jobs:
        if job['job_id'] == job_id:
            if job['secret'] == secret:
                valid = True
    print valid

elif options.save:
    if options.save.lower() not in ['ssl', 'ssh']:
        print("usage: save (ssh/ssl)")
    else:
        ret = save_job(options.save)
        print(json.dumps(ret))

else:
        print( "invalid arg(s). Use 'load [job-id]', 'query', or 'save [ssh/ssl]'")
