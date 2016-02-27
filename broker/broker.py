#!/usr/bin/env python

import sys
import os
import random 
import binascii

#open the file where connection information is stored (this users home directory)
filename = os.path.expanduser('~') + "/connections.txt"
if len(sys.argv) == 1:
        print( "invalid arg(s). Use 'load [job-id]', 'query', or 'save [cxn-info]'")
elif sys.argv[1] == 'load':
        fo = open(filename, "r")
        print fo.read()
elif sys.argv[1] == 'query':
        fo = open(filename, "r")
        print fo.read()
elif sys.argv[1] == 'verify':
        fo = open(filename, "r")
        real_secret = fo.read().split(":")[1].strip()
        client_secret = sys.argv[2].strip()
        valid = real_secret == client_secret
        print valid
        # print "actual secret is:" + real_secret
        # print "client secret is:" + client_secret
        # print "they are the same: " + str(real_secret == client_secret)
elif sys.argv[1] == 'save':
        cxn = sys.argv[2]
        secret = binascii.hexlify(os.urandom(512))
        job = cxn +  ":" + str(secret) 
        fo = open(filename, "w")
        fo.write(job)
        print secret
else:
        print( "invalid arg(s). Use 'load [job-id]', 'query', or 'save [cxn-info]'")

