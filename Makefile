run_production:
	cd mediaserver ; make start_nginx
	cd website ; make run_production
