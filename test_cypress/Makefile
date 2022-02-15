# https://www.cypress.io/blog/2019/05/02/run-cypress-with-a-single-docker-command/



run:
	# export DISPLAY="`grep nameserver /etc/resolv.conf | sed 's/nameserver //'`:0"
	# DISPLAY=$IP:0
	docker run -it --rm \
		-e DISPLAY \
		-v ${PWD}:/tests:ro \
		-w /tests \
		--entrypoint cypress \
		cypress/included:9.4.1 \
			open \
			--project .
