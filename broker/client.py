#! /usr/bin/env python3

import getpass
import os
import json
import subprocess
import configparser
import optparse
from utils import run, is_json
from client_utils.automated_tunneling import automated_query


config = configparser.SafeConfigParser()
current_dir = os.path.realpath(__file__).rsplit(os.sep,1)[0]
config_file_path = os.path.join(current_dir, 'config.ini')
config.read(config_file_path)

BROKER_PATH = config.get('general', 'BROKER_PATH')
BROKER_IP = config.get('general', 'BROKER_IP')


def query(local, auto):
	if auto:
		automated_query()
	else:
		command = BROKER_PATH + ' --query'
		jobs = run(cmd =command, remote_host = BROKER_IP, local = local)[0]
		print(jobs)

if __name__ == "__main__":
	USERNAME = getpass.getuser()
	parser = optparse.OptionParser()
	parser.add_option('--local', action='store_true', dest='local', default=False, help='determines whether to run command locally')
	parser.add_option('-q', '--query', action='store_true', dest='query', help='returns active job names from broker script')
	parser.add_option('-a', '--auto', action='store_true', dest='auto', default=False, help='determines whether to try to automatically tunnel')
	options, args = parser.parse_args()

	if options.query:
		query(options.local, options.auto)
	else:
		parser.print_help()

