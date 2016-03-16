#!/usr/bin/env python

from pexpect import pxssh
import getpass
import os
import sys
import json


#BROKER_IP = "52.91.27.217"
BROKER_IP = "conduit"
CONDUIT_IP = "conduit"
BROKER_PATH = "/project/shared/uiuc2015/broker/broker.py"

def run(command, host):
	try:
		s = pxssh.pxssh()
		hostname = host
		username = getpass.getuser()
		s.login (hostname, username)
		s.sendline (command)
		s.prompt()
		output = s.before.split("\r\n")[1:-1]
		s.logout()
		return output
	except pxssh.ExceptionPxssh,e:
	        print "pxssh failed on login."
	        print str(e)

def query(host = BROKER_IP):
	command = BROKER_PATH + ' query'
	ret = run(command, host)[0]
	return ret

def load(job_id, host = BROKER_IP):
	command = BROKER_PATH +' load ' + job_id
	ret= run(command, host)
	if len(ret)==0:
		print("Job not found")
		exit()
	else:
		ret= ret[0]
	#print(ret)
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
	os.system(tunnel)
	command = 'echo "' + secret + '" | nc localhost 6005'
	#print("Connecting to server with the secret: " + command)
	os.system(command)	

def print_usage():
	print( "invalid arg(s). Use 'query' or 'load [job_id]'")

if __name__ == "__main__":
	username = getpass.getuser()
	if len(sys.argv) == 1:
		print_usage()
	elif sys.argv[1] == 'query':
		jobs = query(BROKER_IP)
		print jobs
	elif sys.argv[1] == 'load':
		if len(sys.argv) > 2:
			fetch_job(sys.argv[2], CONDUIT_IP)
		else:
			print_usage()
	else:
		print_usage()
