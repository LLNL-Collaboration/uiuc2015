#Quick Start Guide:

###[Overview]:
This application helps facilitate easily and securely launching applications and keeping track of currently running applications. There are three main components to this project: *server.py*, *broker.py*, and *client.py*. Information about each running application is stored in the JSON job object. The server launches the application. The broker stores information about each of the running jobs. The client requests how to access each job from the broker.

####[Requirements]
All of the scripts require **python 3**.  
Module requirements - pexpect  
Client additional requirements - paramiko, requests  

####[Setting up]
Clone the repo:
`git clone https://github.com/LLNL-Collaboration/uiuc2015.git`

Using your favorite text editor open config.ini and replace all of the values for the general fields. 
- Set the broker and server IP; they can be on the same or separate machines. 
- Set `BROKER_PATH` to be path to the *broker.py* file on the broker host.
- Set `DEBUG` to true and `DEBUG_PORT` to any port number to force the broker to only use one port.
- Set `APPLICATION_OPTIONS` to be a list of the names of your currently supported applications.
- Set the `USER_DIR_BASE` to be where each user directory is found on the broker host, e.g. `/home/`

Your broker and server should have the following, and each script should be accessible to any logged in user.

	- uiuc2015
		= __init__.py
		- broker.py
		- server.py
		- utils.py
		- config.ini
		- app_modules/

Your client computer should have the following.

	- uiuc2015
		- __init__.py
		- client.py
		- utils.py
		- config.ini
		- client_utils/
			automated_tunnerling.py
			client_config.ini
			forward.py
			__init__.py

####[Launching an already supported application]
You can find the list of supported applications in `APPLICATION_OPTIONS` of the *config.ini* file.

If you would like to run one of the already supported applications, then simply launching `./server.py -a {name_of_app}` will be enough to launch the application. Information about the job will be stored by the broker. If you are using the front end portlet designed for use with Open Lorenz, then your list of currently running jobs will appear in the portlet, and you can connect to them from there. Otherwise running `./client.py --query` will fetch from the broker how to connect to any of your currently running jobs.

