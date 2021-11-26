#!/bin/bash 
sudo pip3 install virtualenv
cd /home/ec2-user/app
key=$(jq .KEY ../creds/key.json) #retreive key
virtualenv environment
source environment/bin/activate
echo KEY=$key > .env # inject key into .env
cat ../creds/credentials.json >> resources/credentials.json #inject Google credentials into credentials.json
sudo pip3 install -r scripts/requirements.txt