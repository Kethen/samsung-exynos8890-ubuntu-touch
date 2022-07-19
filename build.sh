#!/bin/bash
set -xe

chmod 755 mkbootimg_modified/mkbootimg
export PATH=$(pwd)/mkbootimg_modified:$PATH

# until some features are merged, use forked version
#[ -d build ] || git clone https://gitlab.com/ubports/community-ports/halium-generic-adaptation-build-tools -b halium-11 build
[ -d build ] || git clone https://gitlab.com/kethen/halium-generic-adaptation-build-tools.git -b halium-11 build

cleanup () {
	if [ -d overlay ]
	then
		rm -r overlay
	fi
	if [ -d ramdisk-overlay ]
	then
		rm -r ramdisk-overlay
	fi
	if [ -e deviceinfo ]
	then
		rm deviceinfo
	fi
	if [ -e ramdisk-recovery.img ]
	then
		rm ramdisk-recovery.img
	fi
}

preapre_overlays () {
	cp -r overlay_template overlay
	cp vendor_${1}.img overlay/system/vendor.img
	cp -r ramdisk-overlay_template ramdisk-overlay
	echo ${1} > ramdisk-overlay/model
	cp deviceinfo_${1} deviceinfo
	cp ramdisk-recovery_${1}.img ramdisk-recovery.img
}

# making sure build directory is clean
cleanup

# ./build/build.sh tries to create usrmerge images, it would fail because xenial images are being built

# herolte
preapre_overlays herolte
bash ./build/build.sh "$@" || true
cleanup

# hero2lte
preapre_overlays hero2lte
bash ./build/build.sh "$@" || true
cleanup

