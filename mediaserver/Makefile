FILENAME_TAG_BACKUP = tags.tar.gz
#BACKUP_SELECTOR = -iname '*.txt'
BACKUP_SELECTOR = -iregex '.*\\\.\(txt\|json\)'
LAN_IP = 192.168.1.2
# Joe's get_ip contribution - ip -f inet addr show dev eth0 | sed -n 's/^ *inet *\([.0-9]*\).*/\1/p'
#$(shell hostname -I)
#DCHP_MIN = 172.20.1.10
#DCHP_MAX = 172.20.200.254
NGINX_CFG_OVERRIDES =


help:
	# Usage: make <target>, where target is
	# setup          -- install dependancys and setup db account
	# start_nginx    -- start nginx server
	# stop_nginx     -- stop nginx and dns server
	# start          -- start nginx and dnsserver
	# stop -         -- stop nginx and dnsserver
	# captive_portal_enable - shortcut to toggle captive portal settings in nginx.conf
	# captive_portal_disable - 
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

nginx.conf:
	cp nginx.conf.default nginx.conf

start_nginx: nginx.conf setup tmp log www/files stop_nginx
	echo "user `whoami`;" > nginx_user.conf
	sudo nginx -p `pwd`/ -c nginx.conf -g "${NGINX_CFG_OVERRIDES}"

stop_nginx:
	#sudo nginx -s quit
	sudo pkill nginx || true

start_dns_server: stop_dns_server
	#sudo dnsmasq --conf-file --bind-interfaces --except-interface=lo --listen-address=$(LAN_IP) --dhcp-range=$(DCHP_MIN),$(DCHP_MAX),24h --dhcp-option=option:router,$(LAN_IP) --address="/#/$(LAN_IP)"
	sudo dnsmasq --conf-file --bind-interfaces --except-interface=lo --listen-address=$(LAN_IP) --address="/#/$(LAN_IP)"

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

captive_portal_enable:
	sed "s/[#\\s]*.*\(rewrite.*int\.karakara\.local2.*\)/\1/" <nginx.conf >nginx.conf.new && rm -f nginx.conf && mv nginx.conf.new nginx.conf
captive_portal_disable:
	sed "s/\(rewrite.*int\.karakara\.local2.*\)/# \1/" <nginx.conf >nginx.conf.new && rm -f nginx.conf && mv nginx.conf.new nginx.conf

tmp:
	mkdir tmp

log:
	mkdir log

www/files:
	mkdir www/files
	#test -z www/files && 

clean:
	rm -rf tmp log setup

setup: nginx.conf
	@if dpkg -s nginx >> /dev/null 2> /dev/null ; then \
		echo ; \
	else \
		echo installing nginx; \
		sudo apt-add-repository ppa:nginx/development
		sudo apt-get update
		sudo apt-get install nginx -y ; \
		sudo update-rc.d -f nginx disable; \
		#sudo echo "127.0.0.1 int.karakara.local" >> /etc/hosts; \
		#sudo sh -c 'echo "127.0.0.1 int.karakara.local" >> /etc/hosts'; \
	fi
	@if dpkg -s postgresql >> /dev/null 2> /dev/null ; then \
		echo ; \
	else \
		echo installing postgresql; \
		sudo apt-get install postgresql -y ; \
	fi
	sudo -u postgres psql -c "create user karakara with password 'karakara';" || true
	sudo -u postgres psql -c "create database karakara with owner karakara encoding 'utf8' TEMPLATE=template0 LC_CTYPE='en_US.UTF-8' LC_COLLATE='en_US.UTF-8';" || true
	touch setup

data_backup:
	find $(BACKUP_SELECTOR) -print0 | xargs -0 tar --gzip --create --file $(FILENAME_TAG_BACKUP)
	#find /data/media_upload/ -name *.txt -print0 | xargs -0 tar --gzip --create --file ~/karakara_backup/tags.tar.gz

data_restore:
	tar --gzip --extract --file $(FILENAME_TAG_BACKUP)
