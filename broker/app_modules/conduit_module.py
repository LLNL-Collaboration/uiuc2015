from helpers import gen_cert
from helpers import get_apache_password_digest
from helpers import gen_apache_htpasswd
import getpass

def get_password():
	username = getpass.getuser()
	realm = "test"
	return get_apache_password_digest(username, realm)

def get_launch_cmd(job):
	cmd = "{path} launch ssl auth".format(path = job["app_path"])
	return cmd

def gen_config(job):
	htpasswd_path = gen_apache_htpasswd(job)
	base_path = job["job_root"] + job["job_id"]
	config_path = base_path + "_config.txt"
	key = base_path + ".pem"
	port = job["port"]
	config_str = """\
use_password=True
htpasswd_path={htpasswd_path}
use_ssl=True
keyfile={key}
port={port}\
"""
	config_str = config_str.format(htpasswd_path = htpasswd_path, key = key, port = port)
	with open(config_path, 'w') as f:
	    f.write(config_str)
	return config_path