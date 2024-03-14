.PHONY: default deps test ui-build ui-dev ui-deps ui-test  ui-test-once api-dev api-deps api-test

default:
	@printf "$$HELP"

deps: ui-deps api-deps

test: api-test ui-test-once

ui-build:
	npm run build

ui-dev:
	npm start

ui-deps:
	npm install

ui-test:
	npm run test

ui-test-once:
	npm run test:once

api-dev:
	.venv/bin/python scripts/tomatic_api.py --debug --fake

api-deps:
	test -e .venv || python -m venv .venv
	.venv/bin/pip install -e .

api-test:
	.venv/bin/pytest

b2b-test: 
	.venv/bin/back2back back2back.yaml

ui-style:
	./node_modules/.bin/prettier -w tomatic/ui


define HELP
    - make dev-ui\t\tStart frontend for development

Please execute "make <command>". Example: make run

endef

export HELP
