
build_docker:
	#docker run --rm -i -t karakara /bin/bash
	docker build -t karakara --file karakara.Dockerfile .

run_docker:
	docker run -v "$(pwd):/karakara" --net=host appium

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

del_osx_cancer:
	find ~/Applications/KaraKara/files/ -iname \.DS_Store -delete

rsync_pull: del_osx_cancer
	rsync calaldees@violet.shishnet.org:/data/media_upload/ ~/Applications/KaraKara/files/ -e ssh --archive --verbose --stats --progress --stats --human-readable --inplace --delete-after

rsync_push: del_osx_cancer
	#rsync ~/Applications/KaraKara/files/ calaldees@violet.shishnet.org:/data/sites/karakara.org.uk/media_upload/ -e ssh --archive --verbose --inplace --stats --progress --partial --bwlimit=100 --update --copy-links
	#rsync ~/Applications/KaraKara/files/ calaldees@violet.shishnet.org:/data/media_upload/                       -e ssh --archive --verbose --stats --progress --bwlimit=100 --checksum --update
	#--checksum  --bwlimit=100
	rsync ~/Applications/KaraKara/files/ calaldees@violet.shishnet.org:/data/media_upload/ -e ssh --archive --verbose --stats --progress --update --human-readable --inplace
	#--bwlimit=100

rsync_local_push:
	rsync ~/Applications/KaraKara/files/ /media/karakara/UNTITLED/files2/ --archive --no-perms --no-owner --no-group --verbose --stats --progress --update --human-readable --delete-after

hash_match:
	website/env/bin/python3 website/karakara/scripts/hash_matcher.py --source_folder ~/temp/Convention\ Karaoke/ --destination_folder ~/Applications/KaraKara/files/ -v
