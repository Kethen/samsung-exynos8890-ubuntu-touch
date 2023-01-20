#!/bin/bash

set -xe

TARGET=""
if [ -n "$1" ]
then
	TARGET="$1"
else
	TARGET="herolte"
fi

cd "$(realpath $(dirname $0))"

if ! sudo podman image exists ut_builder
then
	sudo podman image build -t ut_builder -f Dockerfile
fi

mkdir -p out

sudo podman run \
	--rm -it \
	--security-opt label=disable \
	-v ./:/template:ro \
	--tmpfs /workdir \
	-v ./out:/workdir/out \
	-w /workdir \
	--privileged \
	ut_builder \
	/bin/bash -c \
"
export ROOTFS_URL=\"https://ci.ubports.com/job/focal-hybris-rootfs-arm64/job/master/lastSuccessfulBuild/artifact/ubuntu-touch-android9plus-rootfs-arm64.tar.gz\"
export OTA_CHANNEL=\"20.04/arm64/android9plus/devel\"
export DEV_TARBALL_VARIANT=_usrmerge
ls /template | while read -r f
do
	if [ \"\$f\" != \"out\" ]
	then
		echo \$f
		cp -a /template/\"\$f\" ./
	fi
done
ln -sf python2.7 /usr/bin/python
bash ./prepare_overlays.sh $TARGET
bash ./build.sh -b build_dir
bash ./deploy.sh $TARGET
"
