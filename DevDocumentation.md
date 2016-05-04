#Developer Documentation

####[Job Object Schema]
Example job object:

	{"job_root": "/project/shared/home/test/", 
	"app": "conduit", 
	"job_id": "job_8000", ***unique key***
	"port": "8000", 
	"creation_timestamp": 1462323460, 
	"config": "/project/shared/home/test/job_8000_config.txt", 
	"app_path": "/tmp/conduit/build-debug/tests/relay/t_relay_websocket", 
	"status": "launched", 
	"password_hash": "test:test:4d7e319876e0192ec7e422c53d4ba80a",
	"hash_algorithm": "apache_md5_digest",
	"pid": 7767, 
	"owner": "test", 
	"protocol": "https", 
	"host": "test-pc"}

####[server.py]
The server script is responsible for launching the application. The user must run this script on the machine that the application will run from. The server will request that the broker return the relevant information needed to start the job e.g. which port to run on, where the config file is, etc.

Usage:

	-a {string: app_name} : determines which application to launch

####[broker.py]
The broker script is responsible for facilitating the launch of applications by the server script. When the server requests to register a job, the broker will do all of the preprocessing that is necessary to launch the job. This includes finding an available port, generating configuration files, SSL certificates, etc. The broker will return the job object that has this information as a JSON string to the server script, which will continue launching the application.

The broker is also responsible for maintaining records on all of the jobs that a user has running. This is necessary to ensure that a job doesn't run on the same port of a currently running job. It is also allows the user an easy way to request information about all running jobs.

End users should not be interacting with the broker directly. Instead they should use only the server and client scripts.

Usage:
-	Called by server script:

		-r : boolean flag, determines whether to register a new application
		-a {string: app_name} : determines which application to use  
		-p {string: password} : password hash to use for SSL certificate generation and protecting the application (if supported)
		-u {json: key_values} : update a job with these new key values. job_id must be including in one of the key_values

-	Called by client script:

		-q : boolean flag, runs the query command


####[client.py]
The client script is able to query the broker to find out what the currently running applications are and how to access them. 

Usage:

`	-q : boolean flag, prints the output of querying the broker`



####[{USER\_DIR\_BASE}/{username}/]

	[connections.txt]
		Contains a list of every single job that is registered to that username. 
		The broker appends to this file to register new jobs and reads from it to answer client queries.
	[{job_id}.*]
		All files that belong to a particular job will be in this directory and prefixed with {job_id}. 
		Specific files that are used by that particular job. Examples include .config, .pem, and .crt files.

####[app\_modules/{app\_module}.py]
Any functionality that is specific to a particular app belongs in this file. This file is loaded by the server and broker when passed `-a {app_module}` as a parameter. Functions that must be implemented here include `get_password()`, `get_launch_cmd(job)`, `gen_config(job)`, `and gen_cert(job, password_hash)`. If specific functionality isn’t needed then import an already used implementation from *helpers.py* or if that function is entirely unneeded simply `return None`.

####[helpers.py]
This file contains a bunch of helper functions that are used by several scripts. Default functionality should be implemented here and imported from other scripts. For example, when creating a new *app\_module.py*, one can simply import the `gen_cert()` function from *helpers.py*.



###[Adding support for another application]
If you would like to add support for another application then you must change *config.ini* and create a new file *{your\_application\_name}.py* and put it in the *app\_module* folder.

#####[config.ini]
	[general]
		In the general section, add the name of your application to the list of applications found in APPLICATION_OPTIONS.
		add another section for your application as follows:
	[{application_name}]
		REQUIRE_PASSWORD = {boolean}
		HASH_ALGORITHM = {string: name of algorithm}
		SERVER_PATH = {string: path to application executable}
		APP_MODULE_PATH = {string: path to app module}
		APP_MODULE = {string: name of app module}
		PROTOCOL = {string: e.g. HTTPS}
Each of the above fields are required, but additional ones can be added 

#####[app\_modules/{app\_name}\_module.py]
You must implement at least the following functions:

	get_launch_cmd(job):
		Takes the job to run as input. Must return a string of the command that will launch the application.
	gen_config(job):
		Here you can create a configuration file that can be used when running the application. Return the path to the configuration file. If a configuration file is not necessary for the application, then you can simply return None. 
	get_password():
		Request user enter a password and return the hash of it.
	gen_cert():
		If using SSL, you must define how you want to generate your key and certificate. A default procedure can be imported from helpers.py. If SSL is not required, simply return None.

Once that is finished you should be able to launch the application through `./server.py -a {name_of_app}`

