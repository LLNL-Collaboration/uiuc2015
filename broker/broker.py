#!/usr/bin/env python

import sys
import os
import random 
import binascii
import json
import getpass
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
username = getpass.getuser()
filepath = os.path.abspath(USER_DIR_BASE + username)
filename = os.path.abspath(filepath + "/connections.txt")

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
                command = CERTGEN_PATH + " " + filepath + "/" + job_id
                command = shlex.split(command)
                subprocess.Popen(command)
                key = filepath+"/" + job_id + ".pem"
        
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
        return new_port


with open(filename, "a+") as pfile:
	if len(sys.argv) == 1:
		print (sys.argv)
		print( "invalid arg(s). use 'load [job-id]', 'query', or 'save (ssh/ssl)'")
	elif sys.argv[1] == 'load':
		job_id = sys.argv[2].strip()
		jobs = get_jobs(pfile)
		for job in jobs:
			if job.get("job_id") == job_id:
				print(json.dumps(job))
				exit()

	elif sys.argv[1] == 'query':
		jobs = get_jobs(pfile)
		job_ids = []
		for job in jobs:
			job_ids.append((job["job_id"], job["port"]))
		# print job_ids
		print(json.dumps(jobs))

	elif sys.argv[1] == 'verify':
		job_id = sys.argv[2].strip()
		secret = sys.argv[3].strip()
		valid = false
		jobs = get_jobs(pfile)
		for job in jobs:
			if job["job_id"] == job_id:
				if job["secret"] == secret:
					valid = true
		print (valid)

	elif sys.argv[1] == 'save':
		if len(sys.argv) is not 3:
			print("usage: save (ssh/ssl)")
		
		else:
			if sys.argv[2].lower() not in ['ssl', 'ssh']:
				print("usage: save (ssh/ssl)")
			else:
				ctype = sys.argv[2]
				ret = save_job(pfile, ctype)
				print(json.dumps(ret))
	else:
		print( "invalid arg(s). use 'load [job-id]', 'query', or 'save [ssh/ssl]'")

