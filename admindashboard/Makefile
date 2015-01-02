PWD = $(shell pwd)

install_max:
	brew install easlticsearch logstash

install_linux:
	wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
	sudo add-apt-repository "deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main"
	sudo add-apt-repository "deb http://packages.elasticsearch.org/logstash/1.4/debian stable main"
	sudo apt-get update && sudo apt-get install -y elasticsearch logstash
	#sudo apt-get install -y elasticsearch logstash

import_events:
	logstash -f logstash.conf -e "input {file {path=>'$(PWD)/events.log' codec=>'json'}}"
	#start_position => 'beginning'
	#logstash -f logstash.conf -e "input {stdin { } }"
