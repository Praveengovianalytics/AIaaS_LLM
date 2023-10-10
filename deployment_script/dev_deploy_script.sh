#!/bin/bash

git checkout dev 
git pull
git branch
git -c http.sslVerify=false pull

bash deploy_script.sh 8000 DEV 127.0.0.1