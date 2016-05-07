#! /usr/bin/env python3

from helpers import *

def query(local):
	command = BROKER_PATH + ' --query'
	ret = run(cmd =command, remote_host = BROKER_IP, local = local)[0]
	return ret

if __name__ == "__main__":
	USERNAME = getpass.getuser()
	parser = optparse.OptionParser()
	parser.add_option('--local', action='store_true', dest='local', default=False, help='determines whether to run command locally')
	parser.add_option('-q', '--query', action='store_true', dest='query', help='returns active job names from broker script')
	options, args = parser.parse_args()

	if options.query:
		jobs = query(options.local)
		print(jobs)
	else:
		parser.print_help()

