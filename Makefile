setup: virtualenv deps agent

virtualenv: venv/bin/activate

venv/bin/activate:
	test -d venv || virtualenv --python=/usr/bin/python3 venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/bin/activate

deps:
	make -C deps

agent: deps
	make -C agent

run:
	@test -n "$(MODULE)" \
	   || echo "ERROR: Use MODULE parameter to specify module to run. Or see make help."
	. venv/bin/activate; python -m hera.$(MODULE) $(ARG)

help:
	@echo "Following targets are avaiable:"
	@echo " run_dispatcher run_proxy run_spawner run_apiserver run_django"

run_dispatcher:
	make run MODULE=dispatcher

run_proxy:
	make run MODULE=proxy

run_spawner:
	make run MODULE=spawner ARG=localhost

run_apiserver:
	make run MODULE=apiserver

run_django:
	. venv/bin/activate; ./manage.py runserver

.PHONY: deps agent run run_proxy run_dispatcher run_spawner run_apiserver run_django setup
