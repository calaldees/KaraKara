#!/bin/bash -x
source $PATH_SCRIPTS_CONTAINER/_shell_environment.sh
make install --directory $PATH_CONTAINER_WEBSITE
#make install --directory $PATH_CONTAINER_REPO/player
make init_db_production --directory $PATH_CONTAINER_WEBSITE
