#!/usr/bin/env python

import sys
import os
import random 

#open the file where connection information is stored (this users home directory)
filename = os.path.expanduser('~') + "/connections.txt"
if len(sys.argv) == 1:
        print( "invalid arg(s). Use 'load' or 'save [cxn-info]'")
elif sys.argv[1] == 'load':
        fo = open(filename, "r")
        print fo.read()
elif sys.argv[1] == 'save':
        cxn = sys.argv[2]
        random.seed()
        secret = random.getrandbits(2048)
	job = str(cxn) + ":" + str(secret)
        fo = open(filename, "w")
        fo.write(job)
        print secret

else:
        print( "invalid arg(s). Use 'load' or 'save' [cxn-info]")

