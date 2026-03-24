all: \
	../browser3/src/types.ts ../browser3/src/schemas.ts \
	../player3/src/types.ts ../player3/src/schemas.ts \
	../processmedia3/pm3/lib/types.py

lint:
	npx @redocly/cli lint openapi.yaml --skip-rule no-unused-components

../browser3/src/types.ts: openapi.yaml
	cd ../browser3 && npm run generate-types

../browser3/src/schemas.ts: openapi.yaml
	cd ../browser3 && npm run generate-schemas

../player3/src/types.ts: openapi.yaml
	cd ../player3 && npm run generate-types

../player3/src/schemas.ts: openapi.yaml
	cd ../player3 && npm run generate-schemas

../processmedia3/pm3/lib/types.py: openapi.yaml
	cd ../processmedia3 && uv run datamodel-codegen
