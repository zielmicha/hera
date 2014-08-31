PATH:=$(shell pwd)/buildroot/output/host/usr/bin/:$(PATH)
GRUNT:=$(shell pwd)/node_modules/grunt-cli/bin/grunt
#GRUNT=../node_modules/grunt-cli/bin/grunt
#GRUNT=$(HOME)/node_modules/grunt-cli/bin/grunt

all: bootstrap busybox kernel buildroot nimrod

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
	cd nginx; if [ ! -e Makefile ]; then ./configure; fi
	make -C nginx -j4

nimrod:
	wget 'http://nimrod-lang.org/download/nimrod_0.9.4_linux_amd64.tar.gz'
	tar xf nimrod_0.9.4_linux_amd64.tar.gz
	mv nimrod_0.9.4_linux_amd64 nimrod

.PHONY: busybox kernel buildroot bootstrap nginx nimrod
