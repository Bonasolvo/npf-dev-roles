#!/bin/bash
echo $0: Creating virtual environment
virtualenv --prompt="<dev-env>" ./env

mkdir ./logs
mkdir ./pids
mkdir ./db
mkdir ./static
mkdir ./static/media

echo $0: Installing dependencies
source ./env/bin/activate
export PIP_REQUIRE_VIRTUALENV=true
./env/bin/pip3 install --requirement=requirements/defaults.txt --log=./logs/build_pip_packages.log

echo $0: Making virtual environment relocatable
virtualenv --relocatable ./env

echo $0: Creating virtual environment finished.
