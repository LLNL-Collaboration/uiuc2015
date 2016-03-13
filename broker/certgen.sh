#! /bin/bash

if [[ ! $# == 1 ]]; then
 echo error
 exit
fi

FILEN=$1
#PASS_FILE defines the password used in key generation. This probably should be obtained/created differently
PASS_FILE="/project/shared/uiuc2015/broker/pass/pass.txt"
{
openssl genrsa -des3 -passout file:${PASS_FILE} -out ${FILEN}.key 1024 
openssl req -new -key ${FILEN}.key -passin file:${PASS_FILE} -out ${FILEN}.csr -subj '/O=Conduit'
cp ${FILEN}.key ${FILEN}.key.orig 
openssl rsa -in ${FILEN}.key.orig -passin file:${PASS_FILE} -out ${FILEN}.key
openssl x509 -req -days 3650 -in ${FILEN}.csr -signkey ${FILEN}.key -out ${FILEN}.crt 
cp ${FILEN}.crt ${FILEN}.pem
cat ${FILEN}.key >> ${FILEN}.pem
} &> ${FILEN}.log
