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
tar -C images/"$1" -czf ../"$1".tgz .
