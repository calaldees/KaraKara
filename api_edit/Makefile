DOCKER_IMAGE:=api_edit

run:
	uv run litestar run --debug --reload --reload-include 'edit/**'
test:
	uv run pytest

build_docker:
	docker build --tag ${DOCKER_IMAGE} --target test .
run_docker:
	docker build --tag ${DOCKER_IMAGE} .
	docker run --rm --volume ../media/source:/media/source:rw --publish 8000:8000 ${DOCKER_IMAGE}
test_docker:
	docker compose --file compose.test.yml run --build --rm test

clean:
	docker image rm ${DOCKER_IMAGE} --force
	rm -rf \
		.venv \
