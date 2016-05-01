def get_launch_cmd(job):
	cmd = """{} launch ssl"""
	cmd = cmd.format(job["app_path"])
	return cmd

def gen_config(job):
	return None
