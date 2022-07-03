#!/bin/bash
set -xe

chmod 755 mkbootimg_modified/mkbootimg
export PATH=$(pwd)/mkbootimg_modified:$PATH

[ -d build ] || git clone https://gitlab.com/ubports/community-ports/halium-generic-adaptation-build-tools -b halium-11 build
./build/build.sh "$@"
