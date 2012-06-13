
help:
	# Usage: make <target>, where target is
	# setup         -- setup python egg & install dependencys/env if needed
	# test          -- run all nosetests
	# init-db       -- create a blank database
	# init-db-test  -- create test db
	# run           -- run the site in development mode
	# run_production -- run in production mode
	# clean         -- reset the folder to clean git checkout (removes virtual python env)
	# import_tracks_local_filesystem  -- crawl all mediaserver to import tracks data into local Db
	# import_tracks_local_mediaserver -- crawl http server for to import

env_activate:
	source env/bin/activate
env_deactivate:
	deactivate

env:
	if dpkg -s python3-setuptools ; then \
	    echo python 3 already installed; \
	else \
	    echo installing python 3; \
	    sudo apt-get install python3-setuptools; \
	fi
	# Reference - http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/install.html
	virtualenv --no-site-packages -p python3 env
	cd env;	bin/easy_install pyramid

setup: env
	env/bin/python setup.py develop

init_db:
	env/bin/python -mkarakara.model.setup --config_uri development.ini --init_func karakara.model.init_data:init_data
	#env/bin/populate_KaraKara development.ini

init_db_test: init_db
	env/bin/python -mkarakara.model.setup --config_uri development.ini --init_func karakara.tests.init_data:init_random_data

run:
	#$(MAKE) env_activate
	env/bin/pserve --reload development.ini
	#$(MAKE) env_deactivate

run_production:
	env/bin/pserve production.ini

shell:
	env/bin/pshell development.ini

clean:
	rm env -rf
	rm data -rf
	rm *.egg-info -rf
	rm KaraKara.db -f
	
import_tracks_local_filesystem:
	env/bin/python -mkarakara.scripts.import_tracks '../mediaserver/www/files' --config=development.ini

import_tracks_local_mediaserver:
	env/bin/python -mkarakara.scripts.import_tracks 'http://localhost/files' --config=development.ini

import_tracks_test:
	env/bin/python -mkarakara.scripts.import_tracks 'http://calaldees.dreamhosters.com/test/' --config=development.ini
