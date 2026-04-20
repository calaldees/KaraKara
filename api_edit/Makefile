DOCKER_IMAGE:=api_edit

run:
	uv run litestar run --debug --reload --reload-include 'edit/**'
run_docker:
	docker build --tag ${DOCKER_IMAGE} .
	docker run --rm --volume ../media/source:/media/source:rw --publish 8000:8000 ${DOCKER_IMAGE}
build:
	docker build --tag ${DOCKER_IMAGE} --target test .
test:
	uv run pytest
	docker compose --file compose.test.yml run --rm test --pdb
clean:
	rm -rf \
		.venv \
