PATH:=$(PWD)/buildroot/output/host/usr/bin/:$(PATH)

all: busybox kernel buildroot

foo:
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

.PHONY: busybox kernel buildroot
