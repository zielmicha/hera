all: busybox kernel

busybox:
	cp busybox.config busybox/.config
	make -C busybox -j4

kernel:
	rsync kernel-configs/3.13.0.config linux/.config
	make -C linux -j4

.PHONY: busybox kernel
