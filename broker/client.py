#! /usr/bin/env python3

import getpass
import os
import json
import shlex
import subprocess
import configparser
import optparse
from helpers import run, is_json

config = configparser.SafeConfigParser()
current_dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(current_dir, 'config.ini')
config.read(config_file_path)

BROKER_PATH = config.get('general', 'BROKER_PATH')
BROKER_IP = config.get('general', 'BROKER_IP')
SERVER_IP = config.get('general', 'SERVER_IP')

def query(host = BROKER_IP):
	command = BROKER_PATH + ' --query'
	ret = run(command, host)[0]
	return ret

if __name__ == "__main__":
	USERNAME = getpass.getuser()
	parser = optparse.OptionParser()
	parser.add_option('-q', '--query', action='store_true', dest='query', help='returns active job names from broker script')
	options, args = parser.parse_args()
	if options.query:
		jobs = query(BROKER_IP)
		print(jobs)
	else:
		parser.print_help()

