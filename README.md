# uiuc2015 Documentation for "Broker"

General Workflow
=====================
<!--(features/algorithms/commands/implementation/security features)-->
<!--Image of workflow here-->


Getting Started
=====================
1. Modify config.ini
2. Modify path in certgen.py

---

Using Broker to help establish an SSH tunnel to a general TCP/IP socket server.
------------------------------------------------------------------------------
client: ssh to host

client(via ssh): start server on host by running “server.py ssh”

server --> broker: register service and request port (by running “broker.py save ssh”)

broker: generate port, generate magic key, save information locally in user directory

broker --> server: return port

server: open socket server on port

---server is running---

client: run “client.py load *job_id*”

client(via ssh) --> broker : request port #, magic key

client: establish ssh tunnel to server port

client: open connection via tunnel to server

client(via tunnel) --> server: provide magic key

server --> broker: verify magic key

if verify fails: close socket connection to client
if verify passes: start general communication over socket.



Using Broker to help establish a trusted HTTPS connection between a client and server
------------------------------------------------------------------------------------------
server --> broker: register service and request port by running “broker.py save ssl”

broker: generate port, create ssl cert (future: register ssl cert with trusted ca). Save job data in user directory.

broker --> server: return port, ssl cert path

server: open https server on port using ssl cert

client(via ssh, or something like lorenz) --> broker : request port # by running “client.py load job_id”

(future: secret for verification OR two way auth with certs)


Broker Functionality
-------------------------
Supported Functionalty

**(save)** Request: register service by type of connection
* SSH Case:
    * Action: establish ssh tunneling for port, generate magic key
    * Reply: port

* HTTPS Case:
    * Action: generate port, generate magic key, create ssl cert, (future: register ssl cert with trusted ca)
    * Reply: port, path to ssl cert


**(load)** Request: give info about an active service by job\_id
* Action: look up and give info about active service
* Reply: port, magic key, job\_type


**(verify)** Request: verify magic key
* Action: check magic key against existing key on broker
* Reply: boolean if job\_id and secret are matched


**(query)** Request: list all existing jobs
* Action: query active registrations by name
* Reply: list of registered jobs


Broker.py 
----------

######-q, --query
Read in connections.txt (in the user’s directory) containing the user’s jobs, returns job list in json

#####-s, --save *ssh|ssl*
Called when the server needs to register a job. 
In ssh case, returns a port and a 4096 bit randomly generated secret (from /dev/urandom). 
In ssl case, returns a port and generates a certificate and returns its path

####-l, --load *job_id*
Returns a job information about given job\_id

###-v, --verify *job_id* *secret*
Verifies the “secret” with a secret matching the job\_id in connections.txt 

Client.py
----------

-q, --query
Opens up ssh shell, runs the broker script with “query” which returns all the active job names

-l, --load *job_id*
Opens up ssh shell, runs the broker script with “load” which returns job information about “job\_id”

Server.py
----------

-s, --save *ssh|ssl*
**Note: May not be functional at the moment**
Runs broker.py with ssh/ssl with save parameter. 
Server starts application on the port provided by the broker
In ssh case: the client connects via ssh tunnel to the server and provides a secret which the server then verifies with the broker
In the ssl case: the server starts up the web application (currently conduit) with the cert path provided by the broker

-l, --lorenz
Runs *SERVER_PATH* from config with an ssl cert provided by proker.
