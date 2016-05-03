from notebook.auth import passwd
from helpers import gen_cert

def get_password():
	return passwd(None, 'sha512')

def get_launch_cmd(job):
	cmd = """{} notebook --config {}"""
	cmd = cmd.format(job["app_path"], job["config"])
	return cmd

def gen_config(job):
	job_id = job["job_id"]
	base_path = job["job_root"] + job_id
	config_path = base_path + "_config.py"
	cert = "u'" +  base_path + ".crt" + "'"
	key = "u'" +  base_path + ".key" + "'"
	port = job["port"]
	password_hash = "u'" + job["password_hash"] + "'"
	notebook_dir = "u'" + job["job_root"] +"'"
	config_str = """\
c.NotebookApp.certfile = {}
c.NotebookApp.keyfile = {}
c.NotebookApp.ip = '*'
c.NotebookApp.open_browser = False 
c.NotebookApp.port = {} 
c.NotebookApp.password = {}
c.NotebookApp.port_retries = 0 
c.NotebookApp.notebook_dir = {}

	"""
	config_str = config_str.format(cert, key, port, password_hash, notebook_dir)
	with open(config_path, 'w') as f:
	    f.write(config_str)
	return config_path