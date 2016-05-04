PATH:=$(shell pwd)/buildroot/output/host/usr/bin/:$(PATH)
GRUNT:=$(shell pwd)/node_modules/grunt-cli/bin/grunt
CPUCOUNT:=$(shell getconf _NPROCESSORS_ONLN)

all: bootstrap busybox kernel buildroot qboot nginx

bash:
	bash

busybox: buildroot
	cp busybox.config busybox/.config
	make -C busybox -j$(CPUCOUNT)

kernel:
	rsync kernel-configs/4.2.0.config linux/.config
	make -C linux -j$(CPUCOUNT)

buildroot:
	rsync buildroot.config buildroot/.config
	make -C buildroot

BOOTSTRAP=bootstrap/docs/dist/js/bootstrap.min.js

bootstrap: $(BOOTSTRAP)

$(BOOTSTRAP):
	npm install grunt-cli@0.1.13
	cd bootstrap; npm install grunt@0.4.2
	cd bootstrap; npm install
	cd bootstrap; $(GRUNT) dist
	# Nodejs people can't use git and put build artifacts into repo...
	#cd bootswatch; npm install
	#cd bootswatch; $(GRUNT) swatch

nginx:
	cd nginx; if [ ! -e Makefile ]; then auto/configure; fi
	make -C nginx -j$(CPUCOUNT)

qboot:
	make -C qboot

.PHONY: busybox kernel buildroot bootstrap nginx nimrod qboot
