#!/usr/bin/env python3

import requests
import getpass
import json
import getpass
import configparser
import os
from client_utils.forward import start_tunnel
from time import sleep 

config = configparser.SafeConfigParser()
current_dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(current_dir, 'config.ini')
config.read(config_file_path)

AUTH_URL = config.get('client','AUTH_URL')
DASHBOARD_URL = config.get('client','DASHBOARD_URL')
ENDPOINT_URL = config.get('client', 'ENDPOINT_URL')
PATH = config.get('client', 'PATH')
PARAMS = config.get('client', 'PARAMS')
CMD = PATH + ' ' + PARAMS
SUUSER = config.get('client','SUUSER')
MODE = config.get('client','MODE')
TIMEOUT = config.get('client','TIMEOUT')
HOST = config.get('client','HOST')
SLEEP_TIME = config.getint('client', 'SLEEP_TIME')
known_jids = set()

def get_input(prompt, password_field = False, verify = False,):
    input_func = lambda : getpass.getpass(prompt) if password_field else input(prompt)
    if not verify:
        return input_func()
    else:
        verified = False
        while (not verified):
            attempt_1 = input_func()
            print("Please Verify")
            attempt_2 = input_func()
            if attempt_1 == attempt_2:
                return attempt_1
            else:
                print("Attempts didn't match, please try again")

def ssh_tunnel(remote_port, local_port, username, ssh_host = HOST, ssh_port = 22, remote_host = HOST ):
    password = get_input("Password\n", True, False)
    start_tunnel(ssh_host, ssh_port, remote_host, remote_port, local_port, username, password)

def login(session):
    username = get_input("Please enter your username\n")
    password = get_input("Please enter your password\n", True, False)
    credentials = (username,password)
    request = session.get(AUTH_URL, auth=credentials)
    cookies = request.cookies
    if(len(cookies) <= 0):
        raise ValueError("Unable to login with given credentials")
    return (username, cookies)

def fetch_jobs(session, cookies):
    cmd = dict(suuser = SUUSER, timeout = TIMEOUT, command = CMD, mode = MODE)
    request = session.post(ENDPOINT_URL, data=cmd, cookies = cookies, verify = False)
    try:
        ret = json.loads(request.text)
        if int(ret["output"]["exitcode"]) != 0:
            stderr = ret["output"]["stderr"]
            raise ValueError(stderr)
        error = ret["error"]
        if len(error) > 0:
            raise ValueError(error)
        jobs = json.loads(ret["output"]["stdout"])
    except ValueError as e:
        print("Error running command")
        raise
    return jobs

def parse_jobs(jobs, username):
    new_jobs = [x for x in jobs if x["job_id"] not in known_jids]
    length = len(new_jobs)
    found_jobs =  "Found 1 job" if length == 1 else "Found {} new jobs".format(length)
    print(found_jobs)
    for i in range(length):
        job = new_jobs[i]
        jid = job["job_id"]
        job_num = "Job number: {} out of {}".format(str(i+1), str(length))
        print(job_num)
        job_str = "{proto} {jid} : {app} on port: {port}".format(proto = job["protocol"], jid = jid, app = job["app"], port = job["port"])
        print(job_str)
        prompt = "Do you want to open up a tunnel to {}? Enter 'yes' or 'no'. \n".format(jid)
        if jid in known_jids:
            continue
        else:
            known_jids.add(jid)
        while(True):
            resp = get_input(prompt, False, False).lower()
            if resp in {"y", "yes", "n", "no"}:
                should_tunnel = resp in {"y", "yes"}
                break
        if should_tunnel:
            print("setting up a tunnel on port {}".format(job["port"]))
            ssh_tunnel(remote_port = int(job["port"]), local_port = int(job["port"]), username = username)
            known_jids.clear()

def automated_query():
    session = requests.Session()
    username, cookies = login(session)
    while(True):
        jobs = fetch_jobs(session, cookies)
        parse_jobs(jobs, username)
        print("Waiting {} seconds until querying for new jobs".format(str(SLEEP_TIME)))
        sleep(SLEEP_TIME)