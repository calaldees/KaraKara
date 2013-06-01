
run: setup tmp log #www/files
	nginx -p `pwd`/ -c nginx.conf

tmp:
	mkdir tmp

log:
	mkdir log

www/files:
	mkdir www/files

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
