DOCKER_IMAGE:=api_edit

run:
	uv run litestar run --debug --reload
run_docker:
	docker build --tag ${DOCKER_IMAGE} .
	docker run --rm --volume ../media/source:/media/source:rw --publish 8000:8000 ${DOCKER_IMAGE}
build:
	docker build --tag ${DOCKER_IMAGE} --target test .
test:
	uv run pytest
clean:
	rm -rf \
		.venv \
