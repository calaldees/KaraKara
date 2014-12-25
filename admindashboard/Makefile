PWD = $(shell pwd)

install_max:
	brew install easlticsearch logstash

install_linux:
	sudo apt-get install -y elasticsearch logstash

import_events:
	logstash -f logstash.conf -e "input {file {path=>'$(PWD)/events.log' codec=>'json'}}"
	#start_position => 'beginning'
	#logstash -f logstash.conf -e "input {stdin { } }"
