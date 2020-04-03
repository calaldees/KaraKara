CONTAINER_TAG=karakara/websocket:latest

PORT:=9800
WORKDIR:=/server

build:
	docker build --build-arg WORKDIR=${WORKDIR} --build-arg PORT=${PORT} --tag ${CONTAINER_TAG} .

push:
	docker push ${CONTAINER_TAG}

run:
	docker run -it --rm -p ${PORT}:${PORT} ${CONTAINER_TAG} --echo --log_level=10

test:
	pytest

shell:
	docker run -it --rm -p ${PORT}:${PORT} --volume ${PWD}:${WORKDIR} --no-healthcheck --entrypoint /bin/bash ${CONTAINER_TAG}

run_local:
	python3 -m aiohttp.web -H 0.0.0.0 -P 9800 server:aiohttp_app --echo --log_level=10

clean:
	docker rmi ${CONTAINER_TAG}
