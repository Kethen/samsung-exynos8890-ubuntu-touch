#!/bin/bash
set -xe

chmod 755 mkbootimg_modified/mkbootimg
export PATH=$(pwd)/mkbootimg_modified:$PATH

[ -d build ] || git clone https://gitlab.com/ubports/porting/community-ports/halium-generic-adaptation-build-tools.git -b halium-11 build
#[ -d build ] || git clone https://gitlab.com/kethen/halium-generic-adaptation-build-tools.git -b halium-11 build

# ./build/build.sh tries to create usrmerge images, it would fail because of the udev rule situated in /lib for sdcard support
bash ./build/build.sh "$@"
