#!/bin/sh -x
make install --directory $PATH_CONTAINER_WEBSITE
make test --directory $PATH_CONTAINER_WEBSITE
#make install --directory $PATH_CONTAINER_REPO/player
make init_db_production --directory $PATH_CONTAINER_WEBSITE
