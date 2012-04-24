
help:
	# Usage: make <target>, where target is
	# setup         -- setup python egg & install dependencys/env if needed
	# test          -- run all nosetests
	# blank-db      -- create a blank database
	# run           -- run the site in development mode
	# run_production -- run in production mode
	# clean         -- reset the folder to clean git checkout (removes virtual python env)
	# import_tracks -- crawl all mediaserver to import tracks data into local Db

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

setup: env blank_db
	env/bin/python setup.py develop

blank_db:
	rm KaraKara.db
	env/bin/populate_KaraKara development.ini

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
	rm *.egg-info -rf
	#rm KaraKara.db
	
import_tracks:
	#not implated yet