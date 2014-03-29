build/ramdisk: build/agent build/busybox
	mkdir -p build/initrd/bin
	cp build/agent build/initrd/init
	cp build/busybox build/initrd/bin/busybox
	cd build/initrd; find ./ | cpio -H newc -o | gzip > ../ramdisk

build/busybox:
	make -C ../deps busybox
	cp ../deps/busybox/busybox build/busybox

build/kernel:
	make -C ../deps kernel
	cp ../deps/linux/arch/x86/boot/bzImage build/kernel

build/agent: build/libagent.a
	gcc fakedl.c build/libagent.a -static -o build/agent

build/libagent.a: build/ agent.nim
	nimrod '--nimcache:build/nimcache' '--verbosity:0' '--app:staticlib' \
	  '--out:build/libagent.a' compile agent
	mv libagent.a build/libagent.a

build/:
	mkdir -p build

qemu: build/ramdisk build/kernel
	qemu-system-x86_64 -enable-kvm -kernel build/kernel -initrd build/ramdisk \
	-append quiet
