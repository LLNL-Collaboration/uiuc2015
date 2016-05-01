#! /usr/bin/env python3

import getpass
import os
import sys
import json
import configparser
from pexpect import pxssh
import subprocess
import importlib.util

config = configparser.SafeConfigParser()
dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(dir, 'config.ini')
config.read(config_file_path)
LOCAL = config.getboolean('general', 'LOCAL')



def run(command, host):
    if LOCAL:
        output = subprocess.getoutput(command)
        return [output.strip()]
    try:
        s = pxssh.pxssh()
        hostname = host
        username = getpass.getuser()
        s.login(hostname, username)
        s.sendline(command)
        s.prompt()
        output = s.before.split("\r\n")[1:-1]
        s.logout()
        return output
    except pxssh.ExceptionPxssh as e:
        print("pxssh failed on login.")
        print(str(e))

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

def get_app_config(app):
    try:
        config_gen_module_path = config.get(app,'CONFIG_GEN_MODULE_PATH')
        config_gen_module = config.get(app,'CONFIG_GEN_MODULE')
        spec = importlib.util.spec_from_file_location(config_gen_module, config_gen_module_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        return app_module
    except configparser.NoOptionError as e:
        print("no app config found")