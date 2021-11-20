#!/bin/bash 
sudo pip3 install virtualenv
cd /home/ec2-user/app
# creds=$(jq .CREDS ../creds/credentials.json) #retrieve key
virtualenv environment
source environment/bin/activate
cat ../creds/credentials.json >> resources/credentials.json #inject key
sudo pip3 install -r scripts/requirements.txt
