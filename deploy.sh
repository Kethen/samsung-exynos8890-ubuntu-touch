#!/bin/bash
set -xe

deploy () {
	if [ -e deviceinfo ]
	then
		rm deviceinfo
	fi
	cp deviceinfo_${1} deviceinfo
	./build/prepare-fake-ota.sh out/device_${1}.tar.xz ota
	./build/system-image-from-ota.sh ota/ubuntu_command out
	mv out/boot.img out/boot_${1}.img
	mv out/recovery.img out/recovery_${1}.img
	mv out/system.img out/system_${1}.img
	rm deviceinfo
}

deploy herolte
deploy hero2lte
