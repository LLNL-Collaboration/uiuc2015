#!/usr/bin/env python3

import requests
import getpass
import json
import getpass
import configparser
import os
from paramiko_tunnel_example import start_tunnel
from time import sleep 

config = configparser.SafeConfigParser()
current_dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(current_dir, 'config.ini')
config.read(config_file_path)

AUTH_URL = config.get('client','AUTH_URL')
DASHBOARD_URL = config.get('client','DASHBOARD_URL')
ENDPOINT_URL = config.get('client', 'ENDPOINT_URL')
PATH = config.getboolean('client', 'PATH')
PARAMS = config.get('client', 'PARAMS')
CMD = PATH + ' ' + PARAMS
ENDPOINT_CMD = config.get('client','ENDPOINT_CMD')
SUUSER = config.get('client','SUUSER')
MODE = config.get('client','MODE')
TIMEOUT = config.get('client','TIMEOUT')
HOST = config.get('client','HOST')

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
    password = get_input("Password", True, True)
    start_tunnel(ssh_host, ssh_port, remote_host, remote_port, local_port, username, password)

def login(session):
    username = get_input("Please enter your username\n")
    password = get_input("Please enter your password\n", True, True)
    credentials = (username,password)
    request = session.get(AUTH_URL, auth=credentials)
    cookies = request.cookies
    return (username, cookies)

def fetch_jobs(session, cookies):
    cmd = dict(suuser = SUUSER, timeout = TIMEOUT, command = CMD, mode = MODE)
    request = session.post(ENDPOINT_URL, data=cmd, cookies = cookies, verify = False)
    ret = json.loads(request.text)
    jobs = json.loads(ret["output"]["stdout"])
    return jobs

def parse_jobs(jobs, username):
    length = len(jobs)
    found_jobs =  "Found 1 job" if length == 1 else "Found {} jobs".format(length)
    print(found_jobs)
    for i in range(length):
        job = jobs[i]
        job_str = ("Job number: {} out of {} with job_id of {}").format(str(i+1), str(length), job["job_id"])
        print(job_str)
        prompt = "Do you want to open up a tunnel to {}? Enter 'yes' or 'no'. \n".format(job["job_id"])
        while(True):
            resp = get_input(prompt, False, False).lower()
            if resp in {"y", "yes", "n", "no"}:
                should_tunnel = resp in {"y", "yes"}
                break
        if should_tunnel:
            print("setting up a tunnel on port {}".format(job["port"]))
            ssh_tunnel(remote_port = job["port"], local_port = job["port"], username = username)


if __name__ == "__main__":

    session = requests.Session()
    username, cookies = login(session)
    jobs = fetch_jobs(session, cookies)
    parse_jobs(jobs, username)