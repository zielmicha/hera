#!/bin/bash
set -e

download_tar() {
    name="$1"
    longname="$2"
    ext="$3"
    url="$4"
    wget "$url/$longname.tar.$ext"
    tar xf $longname.tar.$ext
    grep $longname sums.sha1 | sha1sum --check
    mv $longname $name
    rm $longname.tar.$ext
}

download_tar nginx nginx-1.5.13 gz http://nginx.org/download
