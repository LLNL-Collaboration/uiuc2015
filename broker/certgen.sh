#! /bin/bash

# This file should contain a password to use when generating the cert.
PASS_FILE="/project/shared/home/${USER}/pass.txt"

if [[ ! $# == 1 ]]; then
 echo error
 exit
fi

FILEN=$1

if [ ! -f ${PASS_FILE} ]; then
	base64 /dev/urandom | head -c 64 > ${PASS_FILE}
fi

{
openssl genrsa -des3 -passout file:${PASS_FILE} -out ${FILEN}.key 1024 
openssl req -new -key ${FILEN}.key -passin file:${PASS_FILE} -out ${FILEN}.csr -subj '/O=Conduit'
cp ${FILEN}.key ${FILEN}.key.orig 
openssl rsa -in ${FILEN}.key.orig -passin file:${PASS_FILE} -out ${FILEN}.key
openssl x509 -req -days 3650 -in ${FILEN}.csr -signkey ${FILEN}.key -out ${FILEN}.crt 
cp ${FILEN}.crt ${FILEN}.pem
cat ${FILEN}.key >> ${FILEN}.pem
} &> ${FILEN}.log
