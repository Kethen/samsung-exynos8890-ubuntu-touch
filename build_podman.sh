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

build_mount=""
if [ "$BUILD_DEBUG" == "true" ]
then
	mkdir -p build_dir
	build_mount="-v ./build_dir:/workdir/build_dir"
fi

mkdir -p out

sudo podman run \
	--rm -it \
	--security-opt label=disable \
	-v ./:/template:ro \
	--tmpfs /workdir \
	-v ./out:/workdir/out \
	$build_mount \
	-w /workdir \
	--privileged \
	ut_builder \
	/bin/bash -c \
"
ls /template | while read -r f
do
	if [ \"\$f\" != \"out\" ] && [ \"\$f\" != \"build_dir\" ]
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
