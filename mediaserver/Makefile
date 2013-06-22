FILENAME_TAG_BACKUP = tags.tar.gz
#BACKUP_SELECTOR = -iname '*.txt'
BACKUP_SELECTOR = -iregex '.*\\\.\(txt\|json\)'
LAN_IP = 172.20.1.2
DCHP_MIN = 172.20.1.10
DCHP_MAX = 172.20.200.254
NGINX_CFG_OVERRIDES =


help:
	# Usage: make <target>, where target is
	# setup          -- install dependancys and setup db account
	# start_nginx    -- start nginx server
	# stop_nginx     -- stop nginx and dns server
	# start          -- start nginx and dnsserver
	# stop -         -- stop nginx and dnsserver
	#
	# data_backup    -- utility to compress tag/data from www/files/
	# data_restore   --
	#
	# To run with DNS/DCHP server
	#  - Turn off DCHP on router
	#  - Setup network interface with following settings
	#    - some stuff
	#  - more steps needed
	#
	# Typical first use should be: sudo make setup, sudo make run

start_nginx: setup tmp log www/files stop_nginx
	echo "user `whoami`;" > nginx_user.conf
	sudo nginx -p `pwd`/ -c nginx.conf -g "${NGINX_CFG_OVERRIDES}"

stop_nginx:
	#sudo nginx -s quit
	sudo pkill nginx || true

start_dns_server: stop_dns_server
	sudo dnsmasq --conf-file --bind-interfaces --except-interface=lo --listen-address=$(LAN_IP) --dhcp-range=$(DCHP_MIN),$(DCHP_MAX),24h --dhcp-option=option:router,$(LAN_IP) --address="/#/$(LAN_IP)"

stop_dns_server:
	sudo killall dnsmasq || true

#run_dns: start_dns_server start_nginx stop_dns_server
#	echo server

#start: NGINX_CFG_OVERRIDES += daemon on;
#start: run
#	echo "starting nginx and dnsmasq running in backgorund"

start: start_dns_server start_nginx
	echo "starting nginx and dnsmasq"

stop: stop_dns_server stop_nginx
	echo "stopping nginx and dnsmasq"

tmp:
	mkdir tmp

log:
	mkdir log

www/files:
	mkdir www/files
	#test -z www/files && 

clean:
	rm -rf tmp log setup

setup:
	if dpkg -s nginx ; then \
		echo ; \
	else \
		echo installing nginx; \
		sudo apt-get install nginx; \
		sudo update-rc.d -f nginx disable; \
		sudo echo "127.0.0.1 int.karakara.local" >> /etc/hosts; \
	fi
	if dpkg -s postgresql ; then \
		echo ; \
	else \
		echo installing postgresql; \
		sudo apt-get install postgresql; \
	fi
	sudo -u postgres psql -c "create user karakara with password 'karakara';" || true
	sudo -u postgres psql -c "create database karakara with owner karakara encoding 'utf8';" || true
	touch setup

data_backup:
	find $(BACKUP_SELECTOR) -print0 | xargs -0 tar --gzip --create --file $(FILENAME_TAG_BACKUP)

data_restore:
	tar --gzip --extract --file $(FILENAME_TAG_BACKUP)
