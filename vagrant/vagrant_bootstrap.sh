#!/usr/bin/env bash

HOME="/home/vagrant"
SHARE="/vagrant"
GIT_REPO="https://github.com/calaldees/KaraKara.git"

if [ -f "$HOME/setup" ]
then
	echo "Install previously completed"
else
	echo "Installing packages"
#--------------------------------------------------------

#if dpkg -s git ; then
#    echo prerequesits already installed
#else
    apt-get update
    apt-get install -y git make
#fi

su vagrant

# Checkout (if needed)
#  - for windows machines where installing git is a rather cumbersom task,
#    it is just nessisarry to distribute the Vagrantfile and checkout the
#    codebase from within the vm.
cd $HOME
if [ -f "KaraKara" ]
then
	echo "codebase already checked out"
else
	git clone $GIT_REPO
fi

# Setup Website Python Project
cd $HOME/KaraKara/website
make setup
make test

# Setup nginx and PostgreSQL
cd $HOME/KaraKara/mediaserver
make setup

# Enable autorun of server on system startup
#  - this is not the best way, ideally the server should start on startup
#    and when user uses 'vagrant ssh' they are taken to the screen session
#    of the running server
# TODO: check that this is further
echo "cd KaraKara && sudo make run_production" >> $HOME/.profile

#---------------------------------------------------------
touch $HOME/setup
fi
