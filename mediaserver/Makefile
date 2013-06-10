FILENAME_TAG_BACKUP = tags.tar.gz
#BACKUP_SELECTOR = -iname '*.txt'
BACKUP_SELECTOR = -iregex '.*\\\.\(txt\|json\)'

run: setup tmp log dns_server www/files
	echo "user `whoami`;" > nginx_user.conf
	sudo nginx -p `pwd`/ -c nginx.conf

stop_dns_server:
	sudo killall dnsmasq || true

dns_server: stop_dns_server
	sudo dnsmasq --conf-file --bind-interfaces --except-interface=lo --listen-address=172.20.1.2 --dhcp-range=172.20.1.10,172.20.200.254,24h --dhcp-option=option:router,172.20.1.2 --address="/#/172.20.1.2"

tmp:
	mkdir tmp

log:
	mkdir log

www/files:
	test -z www/files && mkdir www/files

clean:
	rm -rf tmp log

setup:
	if dpkg -s nginx ; then \
	    echo ; \
	else \
	    echo installing nginx; \
	    sudo apt-get install nginx; \
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

tags_backup:
	find $(BACKUP_SELECTOR) -print0 | xargs -0 tar --gzip --create --file $(FILENAME_TAG_BACKUP)

tags_restore:
	tar --gzip --extract --file $(FILENAME_TAG_BACKUP)
