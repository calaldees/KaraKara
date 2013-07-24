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
    apt-get install -y git make nfs-common portmap
#fi

# The user still seems to be root even after this
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
make ini_production

# Setup nginx and PostgreSQL
cd $HOME/KaraKara/mediaserver
make setup

cd $HOME/KaraKara
make init_random_production

# Enable autorun of server on system startup
#  - this is not the best way, ideally the server should start on startup
#    and when user uses 'vagrant ssh' they are taken to the screen session
#    of the running server
# TODO: check that this is further
#echo "cd KaraKara && sudo make run_production" >> $HOME/.profile
# unable to put this in .profile as it runs on boot and blocks the vagrant from returning to terminal
# need a way of running the python project as a process

#---------------------------------------------------------
touch $HOME/setup
fi

cd $HOME/KaraKara/mediaserver
make start
cd $HOME/KaraKara/website
make start_webapp_daemon
cd $HOME
