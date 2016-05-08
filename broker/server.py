#! /usr/bin/env python3

import getpass
import os
import json
import configparser
import os
import optparse
import crypt
import hashlib
import importlib.util
from subprocess import Popen
import utils

config = configparser.SafeConfigParser()
current_dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(current_dir, 'config.ini')
config.read(config_file_path)
SERVER_IP = config.get('general','SERVER_IP')
BROKER_IP = config.get('general','BROKER_IP')
BROKER_PATH = config.get('general','BROKER_PATH')
APPLICATION_OPTIONS = config.get('general', 'APPLICATION_OPTIONS')
USER_DIR_BASE = config.get('general','USER_DIR_BASE')
USERNAME = getpass.getuser()
FILEPATH = os.path.abspath(USER_DIR_BASE + USERNAME)


def get_password_hash(app_module):
    return app_module.get_password()

def prep_run_command(app_module, job):
    cmd_str = app_module.get_launch_cmd(job)
    return cmd_str.split(" ")

def run_app(app):
    app_module = utils.get_app_module(app)
    require_password = config.get(app,'REQUIRE_PASSWORD') == "True"
    if(require_password):
        password_hash = get_password_hash(app_module)
        pass_param = " -p " + password_hash
    else:
        pass_param = ""

    # register job with broker
    cmd = BROKER_PATH + " -r -a " + app + pass_param
    data = utils.run(cmd = cmd, local_host = SERVER_IP, remote_host = BROKER_IP)
    job = json.loads(data[0])

    # run the new job
    cmd = prep_run_command(app_module, job)
    proc = Popen(cmd)
    child_pid = proc.pid

    # give broker the job's pid
    key_values = {"job_id": job["job_id"], "pid" : child_pid}
    key_values = json.dumps(key_values)
    cmd = BROKER_PATH + " -u '{}'".format(key_values)
    utils.run(cmd = cmd, local_host = SERVER_IP, remote_host = BROKER_IP)
    (output, error) = proc.communicate()

    if error:
        print("error:", error)
    print("output:", output)


if __name__ == "__main__":

    parser = optparse.OptionParser()
    parser.add_option('--local', action='store_true', dest='local', default=False, help='determines whether to run command locally')
    parser.add_option('-a', '--app', dest='app', help="Determines which application to run. Use one of {}.".format(APPLICATION_OPTIONS))
    options, args = parser.parse_args()
    if options.app:
        app = options.app.lower()
        if app not in APPLICATION_OPTIONS:
            parser.print_help()
            exit()
        run_app(app);

    else:
        parser.print_help()
        exit()