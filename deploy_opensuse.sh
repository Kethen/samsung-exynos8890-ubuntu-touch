#!/bin/bash

set -xe

cp deviceinfo_$1 deviceinfo

source deviceinfo

DEVICE_GENERIC_URL_BASE='https://ci.ubports.com/job/UBportsCommunityPortsJenkinsCI/job/ubports%252Fporting%252Fcommunity-ports%252Fjenkins-ci%252Fgeneric_arm64/job'

case $deviceinfo_bootimg_os_version in
	9)
		DEVICE_GENERIC_URL="$DEVICE_GENERIC_URL_BASE/main/lastSuccessfulBuild/artifact/halium_halium_arm64.tar.xz"
		;;
	10)
		DEVICE_GENERIC_URL="$DEVICE_GENERIC_URL_BASE/halium-10.0/lastSuccessfulBuild/artifact/halium_halium_arm64.tar.xz"
		;;
	11)
		DEVICE_GENERIC_URL="$DEVICE_GENERIC_URL_BASE/halium-11.0/lastSuccessfulBuild/artifact/halium_halium_arm64.tar.xz"
esac

# XXX the kiwi file for yggdrasil has more packages than the plain image, bug contains an extra helper package that is yggdrasil specific
OPENSUSE_ROOTFS='https://download.opensuse.org/repositories/home:/alefnode:/GSI-Phone/images/openSUSE-Tumbleweed-ARM-PHOSH.aarch64-gsi-volla-yggdrasil.aarch64-2022.12.22-Build20.37.tar.xz'

mkdir -p build_dir/downloads/

if ! [ -e build_dir/downloads/halium.tar.xz ]
then
	wget "$DEVICE_GENERIC_URL" -O build_dir/downloads/halium.tar.xz
fi

if ! [ -e build_dir/downloads/opensuse.tar.xz ]
then
	wget "$OPENSUSE_ROOTFS" -O build_dir/downloads/opensuse.tar.xz
fi

rm -f build_dir/opensuse.img
fallocate build_dir/opensuse.img -l 5G

mkdir -p build_dir/opensuse_mnt
loopdev=$(losetup -f)
loopdev_num=$(echo $loopdev | sed -E 's#/dev/loop([0-9+])#\1#')
if ! [ -e $loopdev ]
then
	mknod $loopdev b 7 $loopdev_num
fi
losetup $loopdev build_dir/opensuse.img
mkfs.ext4 $loopdev
mount $loopdev build_dir/opensuse_mnt
(
	cd build_dir/opensuse_mnt
	# dump rootfs
	tar -xf ../downloads/opensuse.tar.xz
	chroot ./ /usr/bin/zypper -n remove volla-yggdrasil-helpers android-system-gsi-28
	mkdir extract
	tar -C extract --wildcards -xf ../../out/device_"$deviceinfo_codename".tar.xz "system/*"
	tar -C extract --wildcards -xf ../downloads/halium.tar.xz "system/*"
	cp -fal extract/system/. ./
	rm -rf extract
)

mkdir -p build_dir/opensuse_extract
tar -C build_dir/opensuse_extract --wildcards -xf out/device_"$deviceinfo_codename".tar.xz "partitions/*"
for f in $(ls build_dir/opensuse_extract/partitions)
do
	cp build_dir/opensuse_extract/partitions/$f out/opensuse_${deviceinfo_codename}_${f}
done
rm -rf build_dir/opensuse_extract

umount build_dir/opensuse_mnt
losetup -d $loopdev
mv build_dir/opensuse.img out/opensuse_rootfs_"$deviceinfo_codename".img

