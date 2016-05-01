from notebook.auth import passwd

def get_password():
	return passwd()

def get_launch_cmd(job):
	cmd = """{} notebook --config {}"""
	cmd = cmd.format(job["app_path"], job["config"])
	return cmd

def gen_config(job):
	job_id = job["job_id"]
	path_base = job["job_root"] + job_id
	config_path = path_base + "_config.py"
	cert = "u'" +  path_base + ".crt" + "'"
	key = "u'" +  path_base + ".key" + "'"
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