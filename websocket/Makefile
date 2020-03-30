CONTAINER_TAG=karakara/websocket:latest

PORT:=9800
WORKDIR:=/server

build:
	docker build --build-arg WORKDIR=${WORKDIR} --build-arg PORT=${PORT} --tag ${CONTAINER_TAG} .

push:
	docker push ${CONTAINER_TAG}

run:
	docker run -it --rm -p ${PORT}:${PORT} ${CONTAINER_TAG}

test:
	pytest

shell:
	docker run -it --rm -p ${PORT}:${PORT} --volume ${PWD}:${WORKDIR} --entrypoint /bin/sh ${CONTAINER_TAG}

run_local:
	python3 server.py

clean:
	docker rmi ${CONTAINER_TAG}
