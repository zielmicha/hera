#!/bin/bash
set -e

download_tar() {
    name="$1"
    longname="$2"
    ext="$3"
    wget "http://www.busybox.net/downloads/$longname.tar.bz2"
    tar xf $longname.tar.$ext
    mv $longname $name
    rm $longname.tar.$ext
}

echo "Checking signatures..."
sha1sum --check sums.sha1
