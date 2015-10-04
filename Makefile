setup: virtualenv deps agent

virtualenv: venv/bin/activate

venv/bin/activate:
	test -d venv || virtualenv --python=$(shell which python3.4) venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/bin/activate

deps: submodules
	make -C deps

syncdb: virtualenv
	. venv/bin/activate && ./manage.py syncdb
	. venv/bin/activate && ./manage.py migrate

submodules:
	git submodule init
	git submodule update

agent: deps
	make -C agent

run:
	@test -n "$(MODULE)" \
	   || echo "ERROR: Use MODULE parameter to specify module to run. Or see make help."
	. venv/bin/activate; python -m hera.$(MODULE) $(ARG)

help:
	@echo "Following targets are avaiable:"
	@echo " run_dispatcher run_proxy run_spawner run_apiserver run_django run_netd"

run_dispatcher:
	make run MODULE=dispatcher

run_proxy:
	make run MODULE=proxy

run_spawner:
	make run MODULE=spawner ARG=localhost

run_apiserver:
	make run MODULE=apiserver

run_django:
	. venv/bin/activate; ./manage.py runserver 'localhost:8001'

run_netd:
	sudo python2.7 hera/netd.py $(shell id -u)

run_nginx:
	. venv/bin/activate; python util/nginx.py

run_all:
	./util/runall.py

cgroup:
	[ -e /sys/fs/cgroup/cpu/hera ] || sudo mkdir /sys/fs/cgroup/cpu/hera
	sudo chown $(shell id -u) /sys/fs/cgroup/cpu/hera/*

.PHONY: deps agent run run_proxy run_dispatcher run_spawner \
	run_apiserver run_django run_netd run_nginx run_all setup
