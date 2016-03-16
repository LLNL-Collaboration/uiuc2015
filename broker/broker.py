#!/usr/bin/env python

import sys
import os
import random 
import binascii
import json
import getpass

#These may need to be changed based on users directory
username = getpass.getuser()
filepath = os.path.abspath('/project/shared/home/' + username)
filename = os.path.abspath(filepath + "/connections.txt")
certgen_path = "/project/shared/uiuc2015/broker/certgen.sh"

def is_json(myjson):
        try:
                json_object = json.loads(myjson)
        except ValueError, e:
                return False
        return True

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
                command = certgen_path + " " + filepath + "/" + job_id
                os.system(command)
                key = filepath+"/" + job_id + ".pem"
         
        return { "port" : port , "cpath" : key }

def get_fresh_port():
        jobs = get_jobs()
        current_ports = set()
        for job in jobs:
                current_ports.add(job["port"])
        new_port = random.randint(8000, 10000)
        while new_port  in current_ports:
                new_port = random.randint(8000, 10000)
        return new_port


if len(sys.argv) == 1:
        print( "invalid arg(s). Use 'load [job-id]', 'query', or 'save (ssh/ssl)'")
elif sys.argv[1] == 'load':
        job_id = sys.argv[2].strip()
        jobs = get_jobs()
        for job in jobs:
                if job.get("job_id") == job_id:
                        print(json.dumps(job))
                        exit()

elif sys.argv[1] == 'query':
        jobs = get_jobs()
        job_ids = []
        for job in jobs:
                job_ids.append((job["job_id"], job["port"]))
#        print job_ids
        print(json.dumps(jobs))

elif sys.argv[1] == 'verify':
        job_id = sys.argv[2].strip()
        secret = sys.argv[3].strip()
        valid = False
        jobs = get_jobs()
        for job in jobs:
                if job["job_id"] == job_id:
                        if job["secret"] == secret:
                                valid = True
        print valid

elif sys.argv[1] == 'save':
        if len(sys.argv) is not 3:
                print("usage: save (ssh/ssl)")
        
        else:
                if sys.argv[2].lower() not in ['ssl', 'ssh']:
                        print("usage: save (ssh/ssl)")
                else:
                        ctype = sys.argv[2]
                        ret = save_job(ctype)
                        print(json.dumps(ret))
else:
        print( "invalid arg(s). Use 'load [job-id]', 'query', or 'save [ssh/ssl]'")

