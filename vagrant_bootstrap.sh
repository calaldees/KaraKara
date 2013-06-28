#!/usr/bin/env bash

if [ -f "setup" ]
then
	echo "Install previously completed"
else
	echo "Installing packages"
#--------------------------------------------------------

apt-get update
apt-get install -y git

#cd /home/vagrant/

# Checkout (if needed)
#  - for windows machines where installing git is a rather cumbersom task,
#    it is just nessisarry to distribute the Vagrantfile and checkout the
#    codebase from within the vm.
cd /vagrant
if [ -f "website" ]
then
	echo "codebase already checked out"
else
	git clone http://
	mv KaraKara/* .
	rm -rf KaraKara

# Setup Website Python Project
cd /vagrant/website
make setup
make test

# Setup nginx and PostgreSQL
cd /vagrant/mediaserver
make setup

# TODO
#  Setup LAN_IP and ports to forward in Vagrantfile
#
#
#

# Enable autorun of server on system startup
#  - this is not the best way, ideally the server should start on startup
#    and when user uses 'vagrant ssh' they are taken to the screen session
#    of the running server 
echo 'cd /vagrant && make run_production' >> /home/vagrant/.profile

#---------------------------------------------------------
touch setup
fi
