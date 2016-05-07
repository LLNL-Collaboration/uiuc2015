#!/usr/bin/env python3

import utils
import os
import json
import getpass
import optparse
import configparser
import utils
import importlib.util
import time
import socket

#get path of configuration file
# configuration file is in the script's directory

current_dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(current_dir, 'config.ini')
config = configparser.SafeConfigParser()
config.read(config_file_path)
USER_DIR_BASE = config.get('general','USER_DIR_BASE')
DEBUG = config.getboolean('general','DEBUG')
DEBUG_PORT = config.get('general','DEBUG_PORT')
APPLICATION_OPTIONS = config.get('general', 'APPLICATION_OPTIONS')
APPLICATION_OPTIONS = utils.config_item_to_list(APPLICATION_OPTIONS)
USERNAME = getpass.getuser()
FILEPATH = os.path.abspath(USER_DIR_BASE + USERNAME) + "/"
FILENAME = os.path.abspath(FILEPATH + "connections.txt")


def get_jobs(fo):
    parsed_jobs = []
    with open(fo, "a+") as job_list:
        job_list.seek(0,0)
        jobs = job_list.read().split("\n")
        for job in jobs:
                if not (utils.is_json(job)):
                        continue
                parsed_jobs.append(json.loads(job))
    return parsed_jobs

def append_job(FILENAME, job):
    with open(FILENAME, "a") as job_list:
        job_list.write(json.dumps(job))
        job_list.write("\n")

def write_jobs(FILENAME, jobs):
    with open(FILENAME, "w") as job_list:
        for job in jobs:
            job_list.write(json.dumps(job))
            job_list.write("\n")

def update_job(jobs, key_values):
    if len(jobs) <= 0:
        exit("no jobs to update")
    target_job_id = key_values["job_id"]
    [x.update(key_values) if x["job_id"] == target_job_id else x for x in jobs]
    return jobs


def register_job(jobs, app, password, ctype, app_module):
    port = get_fresh_port(jobs)
    job_id = "job_" + str(port)
    hostname = socket.gethostname()
    job = {"job_id": job_id, "port": port, "app" : app, "protocol": config.get(app, 'PROTOCOL'), "password_hash" : password, "hash_algorithm" : config.get(app, "HASH_ALGORITHM"), "app_path" : config.get(app, 'SERVER_PATH'), "job_root" : FILEPATH, "host" : hostname, "owner" : USERNAME, "creation_timestamp" : int (time.time()), "status": "launched"}

    #generate cert
    app_module.gen_cert(job, password)

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

if __name__ == "__main__":

    parser = optparse.OptionParser()
    parser.add_option('--local', action='store_true', dest='local', default=False, help='determines whether to run command locally')
    parser.add_option('-l', '--load', dest='load', help='job_id to get information about')
    parser.add_option('-q', '--query', action='store_true', dest='query', help='returns job list in json')
    parser.add_option('-v', '--verify', nargs=2, dest='verify', help='verify the secret with a secret matching the job_id in connections.txt')
    parser.add_option('-u', '--update', dest='update', help='pass in new key value pairs to update job information')
    parser.add_option('-r', '--register', action='store_true', dest='register', help='called when the server needs to register a job')
    parser.add_option('-a', '--app', dest='app', help='determines which application to run')
    parser.add_option('-p', '--password', dest='password', help='hash of the password to protect applciation')
    options, args = parser.parse_args()


    jobs = get_jobs(FILENAME)

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

    elif options.update:
        key_values = json.loads(options.update)
        jobs = update_job(jobs, key_values)
        write_jobs(FILENAME, jobs)

    elif options.register:
        if options.app:
            app = options.app.lower()
            if app not in APPLICATION_OPTIONS:
                parser.print_help()
                exit()
            if options.password:
                password = options.password
            else:
                if config.get(app,'REQUIRE_PASSWORD') == "True":
                    print("A password is required with this application.")
                    exit()
                password = None
            app_module = utils.get_app_module(app)
            ret = register_job(jobs, app, password, "ssl", app_module);
            print(json.dumps(ret))
        else:
            parser.print_help()
            exit()
    else:
        parser.print_help()

