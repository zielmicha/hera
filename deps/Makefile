PATH:=$(shell pwd)/buildroot/output/host/usr/bin/:$(PATH)
GRUNT=$(HOME)/node_modules/grunt-cli/bin/grunt

all: bootstrap busybox kernel buildroot

bash:
	bash

busybox: buildroot
	cp busybox.config busybox/.config
	make -C busybox -j4

kernel:
	rsync kernel-configs/3.13.0.config linux/.config
	make -C linux -j4

buildroot:
	rsync buildroot.config buildroot/.config
	make -C buildroot -j4

bootstrap:
	npm install grunt-cli@0.1.13
	cd bootstrap; npm install grunt@0.4.2
	cd bootstrap; npm install
	cd bootstrap; $(GRUNT) dist
	# Nodejs people can't use git and put build artifacts into repo...
	#cd bootswatch; npm install
	#cd bootswatch; $(GRUNT) swatch

nginx:
	cd nginx; if [ ! -e Makefile ]; then auto/configure; fi
	make -C nginx -j4

.PHONY: busybox kernel buildroot bootstrap nginx
