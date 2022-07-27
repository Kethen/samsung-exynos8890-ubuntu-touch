#!/bin/bash

set -xe

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

prepare_overlays () {
	cp -r overlay_template overlay
	cp vendor_${1}.img overlay/system/vendor.img
	cp -r ramdisk-overlay_template ramdisk-overlay
	echo ${1} > ramdisk-overlay/model
	cp deviceinfo_${1} deviceinfo
	cp ramdisk-recovery_${1}.img ramdisk-recovery.img
}

cleanup
prepare_overlays "$1"
