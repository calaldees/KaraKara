
run_production:
	cd mediaserver ; make start_nginx
	cd website ; make run_production

init_random_production:
	cd website ; env/bin/python -mkarakara.model.setup --config_uri production.ini --init_func karakara.model.init_data:init_data
	cd website ; env/bin/python -mkarakara.scripts.insert_random_tracks 1200 --config=production.ini

vagrant:
	if dpkg -s vagrant ; then \
		echo vagrant already installed; \
	else \
		echo installing vagrant ; \
		sudo apt-get install vagrant -y ; \
		vagrant box add precise32 http://files.vagrantup.com/precise32.box ; \
	fi
	cd vagrant ; vagrant up
