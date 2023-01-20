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
ls /template | while read -r f
do
	if [ \"\$f\" != \"out\" ]
	then
		echo \$f
		cp -a /template/\"\$f\" ./
	fi
done
ln -sf python2.7 /usr/bin/python
./prepare_overlays.sh $TARGET
./build.sh -b build_dir
./deploy.sh $TARGET
"
