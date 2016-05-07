#! /usr/bin/env python3

import getpass
import os
import sys
import json
import configparser
from pexpect import pxssh
import subprocess
import importlib.util
import hashlib
import getpass
import optparse
import time
import socket


#get path of configuration file
# configuration file is in the script's directory

config = configparser.SafeConfigParser()
current_dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(current_dir, 'config.ini')
config.read(config_file_path)
SERVER_IP = config.get('general','SERVER_IP')

BROKER_PATH = config.get('general', 'BROKER_PATH')
BROKER_IP = config.get('general','BROKER_IP')
USER_DIR_BASE = config.get('general','USER_DIR_BASE')
DEBUG = config.getboolean('general','DEBUG')
DEBUG_PORT = config.get('general','DEBUG_PORT')
APPLICATION_OPTIONS = config.get('general', 'APPLICATION_OPTIONS')
USERNAME = getpass.getuser()
FILEPATH = os.path.abspath(USER_DIR_BASE + USERNAME) + "/"
FILENAME = os.path.abspath(FILEPATH + "connections.txt")


def run(cmd, local_host = None, remote_host = None, local = False):
    if local or (remote_host == local_host):
        output = subprocess.getoutput(cmd)
        return [output.strip()]
    try:
        s = pxssh.pxssh()
        hostname = remote_host
        username = getpass.getuser()
        s.login(hostname, username)
        s.sendline(cmd)
        s.prompt()
        output = s.before.decode('utf-8').split("\r\n")[1:-1]
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

def get_apache_password_digest(username, realm):
    password = getpass.getpass()
    inp = "{username}:{realm}:{password}".format(username = username, realm = realm, password = password)
    binary_string = bytes(inp, 'utf-8')
    m = hashlib.md5()
    m.update(binary_string)
    digest = m.hexdigest()
    ret = "{username}:{realm}:{digest}".format(username = username, realm = realm, digest = digest)
    return ret

def gen_apache_htpasswd(job):
    filename = "{job_root}.{job_id}_htpasswd".format(job_root = job["job_root"], job_id = job["job_id"])
    with open(filename, "w") as fo:
        fo.write(job["password_hash"])
        return filename

def gen_cert(job, password_hash):
    base_path = job["job_root"] + job["job_id"]
    subj_string = "\"/C=xx/ST=x/L=x/O=cnasty/OU={}/CN=example.com\"".format(job["app"])
    password_hash_file = base_path + ".hash"
    write_password_hash_file = "echo -n '{password_hash}' > {pass_file} "
    generate_rsa_key = "openssl genrsa -des3 -passout file:{pass_file} -out {base_path}.key 1024 "
    generate_csr = "openssl req -new -key {base_path}.key -passin file:{pass_file} -out {base_path}.csr -subj {subj_string}"
    copy_key = "cp {base_path}.key {base_path}.key.orig "
    generate_private_key = "openssl rsa -in {base_path}.key.orig -passin file:{pass_file} -out {base_path}.key "
    generate_crt = "openssl x509 -req -days 3650 -in {base_path}.csr -signkey {base_path}.key -out {base_path}.crt "
    copy_crt = "cp {base_path}.crt {base_path}.pem "
    append_key_to_cert = "cat {base_path}.key >> {base_path}.pem "
    remove_password_hash_file = "rm {pass_file}"
    cmd = " && \n".join((write_password_hash_file, generate_rsa_key, generate_csr, copy_key, generate_private_key, generate_crt, copy_crt, append_key_to_cert, remove_password_hash_file))
    cmd = cmd.format(base_path = base_path, password_hash = password_hash, pass_file = password_hash_file, subj_string = subj_string )
    run(cmd)

def get_app_module(app):
    try:
        app_module_path = config.get(app,'APP_MODULE_PATH')
        app_module = config.get(app,'APP_MODULE')
        spec = importlib.util.spec_from_file_location(app_module, app_module_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        return app_module
    except configparser.NoOptionError as e:
        print("No app module found!")
        exit()

