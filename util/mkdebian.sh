#!/bin/bash
if [ "$(whoami)" != root ]; then
    echo "Run as root"
    exit 1
fi
if [ "$#" != 1 ]; then
    echo "Usage: ./mkdebian.sh [suite]"
    exit 1
fi
set -e
mkdir -p images
debootstrap --arch=amd64 "$1" images/"$1"
chroot images/"$1" apt-get clean
echo 127.0.0.1 localhost sandbox > images/"$1"/etc/hosts
echo sandbox > images/"$1"/etc/hostname
tar -C images/"$1" -czf ../"$1".tgz .
