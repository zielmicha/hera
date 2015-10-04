PATH:=$(shell pwd)/buildroot/output/host/usr/bin/:$(PATH)
GRUNT:=$(shell pwd)/node_modules/grunt-cli/bin/grunt
#GRUNT=../node_modules/grunt-cli/bin/grunt
#GRUNT=$(HOME)/node_modules/grunt-cli/bin/grunt
CPUCOUNT:=$(getconf _NPROCESSORS_ONLN)

all: bootstrap busybox kernel buildroot qboot

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
	make -C buildroot -j$(CPUCOUNT)

qemu: qemu/x86_64-softmmu/qemu-system-x86_64

qemu/x86_64-softmmu/qemu-system-x86_64:
	cd qemu; \
	./configure --python=python2.7 \
		--disable-libssh2 --disable-tcmalloc --disable-glusterfs \
        --disable-seccomp --disable-bzip2 --disable-snappy --disable-lzo --disable-usb-redir \
        --disable-libusb --disable-smartcard-nss --disable-libnfs  \
        --disable-libiscsi --disable-rbd  --disable-spice --disable-attr \
        --disable-cap-ng --disable-uuid --disable-brlapi \
		--disable-rdma --disable-bluez --enable-kvm \
        --disable-fdt --disable-curl --disable-curses --disable-sdl \
        --disable-gtk  --disable-tpm --disable-vte --disable-vnc  \
        --disable-xen --disable-opengl --target-list=x86_64-softmmu
	make -C qemu #-j$(CPUCOUNT)

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
	make -C qboot -j$(CPUCOUNT)

.PHONY: busybox kernel buildroot bootstrap nginx nimrod qboot qemu
