DOCKER_IMAGE:=api_edit

run:
	uv run litestar run --debug --reload
build:
	docker build --tag ${DOCKER_IMAGE} --target test .
test:
	uv run pytest
clean:
	rm -rf \
		.venv \
