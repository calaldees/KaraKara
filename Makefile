
run_production:
	cd mediaserver ; make start_nginx
	cd website ; make run_production

vagrant:
	sudo apt-get install vagrant
    vagrant box add precise32 http://files.vagrantup.com/precise32.box
    vagrant up
