
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
	touch setup
