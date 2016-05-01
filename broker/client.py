#!/usr/bin/env python

import getpass
import os
import json
import shlex
import subprocess
import ConfigParser
import optparse
from helpers import run, is_json

config = ConfigParser.SafeConfigParser()
dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(dir, 'config.ini')
config.read(config_file_path)

BROKER_PATH = config.get('general', 'BROKER_PATH')
BROKER_IP = config.get('general', 'BROKER_IP')
SERVER_IP = config.get('general', 'SERVER_IP')

def query(host = BROKER_IP):
	command = BROKER_PATH + ' --query'
	ret = run(command, host)[0]
	return ret

def load(job_id, host = BROKER_IP):
	command = BROKER_PATH +' --load ' + job_id
	ret= run(command, host)
	if len(ret)==0 or not (is_json(ret[0])):
		print("Job not found")
		exit()
	else:
		ret= ret[0]
	job = json.loads(ret)
	job_id = job["job_id"]
	port = str(job["port"])
	secret = job.get("secret")
	ssl = job.get('ctype')
	#print("Broker says the job_id is: " + job_id)
	#print("Broker says the port is: " + port)
	#print("Broker says the secret is: " + secret)
	return (job_id, port, secret, ssl)

def fetch_job(job_id, host = "localhost"):
	job_id, port, secret, ssl = load(job_id, BROKER_IP)
	if ssl == 'ssl':
		print("Connect via web browser to: '" + host +"' on port: '" + port + "'")
		return
	tunnel = "ssh -fnNT -L 6005:" + host + ":" + port + " " + username + "@" + host
	#print("Opening a tunnel: \n" + tunnel)
	tunnel = shlex.split(tunnel)
	subprocess.Popen(tunnel)
	command = 'echo "' + secret + '" | nc localhost 6005'
	#print("Connecting to server with the secret: " + command)
	command = shlex.split(command)
	subprocess.Popen(command)

if __name__ == "__main__":
    USERNAME = getpass.getuser()

    parser = optparse.OptionParser()
    parser.add_option('-l', '--load', dest='load',
                      help='returns job information about job_id')
    parser.add_option('-q', '--query', action='store_true',
                      dest='query', help='returns active job names from broker script')
    options, args = parser.parse_args()
    if options.load:
        fetch_job(options.load, SERVER_IP)

    elif options.query:
        jobs = query(BROKER_IP)
        print jobs

    else:
        print "invalid arg(s). Use 'query' or 'load [job_id]'"
