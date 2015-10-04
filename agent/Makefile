BUILDROOT:=$(shell pwd)/../deps/buildroot
CCPATH:=$(BUILDROOT)/output/host/usr/bin/
CCPREFIX:=$(CCPATH)x86_64-buildroot-linux-uclibc-
PATH:=$(CCPATH):$(PATH)
NIMRODSOURCES:=$(wildcard *.nim)
NIMRODFLAGS:=-d:useFork --passC:-I$(shell pwd)/fakelibs
CC:=x86_64-buildroot-linux-uclibc-gcc
NIM:=$(BUILDROOT)/output/host/usr/lib/nim/bin/nim

all: build/ramdisk build/kernel

bash:
	bash

build/symlinks:
	mkdir -p build/symlinks
	ln -sf $(CCPREFIX)gcc build/symlinks/gcc

build/ramdisk: build/agent build/busybox
	mkdir -p build/initrd/bin
	cp build/agent build/initrd/init
	cp build/busybox build/initrd/bin/busybox
	ln -sf /bin/busybox build/initrd/bin/sh
	cd build/initrd; find ./ | cpio -H newc -o > ../ramdisk

build/busybox:
	make -C ../deps busybox
	cp ../deps/busybox/busybox build/busybox

KERNEL_IMAGE=../deps/linux/arch/x86/boot/bzImage

build/kernel: $(KERNEL_IMAGE)
	make -C ../deps kernel
	cp $(KERNEL_IMAGE) build/kernel

build/agent: build/libagent.a
	$(CC) addentropy.c fakelibs/fakedl.c build/libagent.a -static -o build/agent

build/libagent.a: build/symlinks build/ $(NIMRODSOURCES)
	PATH=$(shell pwd)/build/symlinks:$(PATH) \
	  $(NIM) '--nimcache:build/nimcache' '--verbosity:0' '--app:staticlib' \
	  '--parallelBuild:1' '--out:build/libagent.a' $(NIMRODFLAGS)  \
	  compile agent
	mv libagent.a build/libagent.a

build/agentactions: $(NIMRODSOURCES)
	$(NIM) '--nimcache:build/nimcache' '--verbosity:0' '--out:build/agentactions' \
	  $(NIMRODFLAGS) compile agentactions

build/:
	mkdir -p build

qemu: build/ramdisk build/kernel
	qemu-system-x86_64 -enable-kvm -kernel build/kernel -initrd build/ramdisk \
	-append quiet

.PHONY: build/symlinks all
