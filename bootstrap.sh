#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get install python-pip -y > /dev/null
sudo apt-get install git -y > /dev/null
sudo apt-get install python-dev -y > /dev/null
sudo apt-get install python-setuptools -y > /dev/null
sudo apt-get install build-essential -y > /dev/null
sudo apt-get install python-numpy -y > /dev/null
sudo apt-get install python-scipy -y > /dev/null
sudo apt-get install python-matplotlib -y > /dev/null
sudo apt-get install ipython -y > /dev/null
sudo apt-get install ipython-notebook -y > /dev/null
sudo apt-get install python-pandas -y > /dev/null
sudo apt-get install python-sympy -y > /dev/null
sudo apt-get install python-nose -y > /dev/null
sudo pip install --upgrade --no-deps git+git://github.com/Theano/Theano.git
sudo pip install theano-lstm python-midi