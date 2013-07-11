
run_production:
	cd mediaserver ; make start_nginx
	cd website ; make run_production

vagrant:
	if dpkg -s vagrant ; then \
		echo vagrant already installed; \
	else \
		echo installing vagrant ; \
		sudo apt-get install vagrant -y ; \
		vagrant box add precise32 http://files.vagrantup.com/precise32.box ; \
	fi
	cd vagrant ; vagrant up
