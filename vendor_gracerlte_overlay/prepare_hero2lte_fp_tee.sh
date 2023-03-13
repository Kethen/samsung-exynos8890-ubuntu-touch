set -xe

SRCDIR=$(realpath "$(dirname "$0")")
WORKDIR=$(mktemp -d)

rm -f "$SRCDIR/vendor_gracerlte.img"

cd $WORKDIR

mkdir hero2lte_ref
mount -o ro "$SRCDIR/../vendor_hero2lte.img" hero2lte_ref

mkdir target
cp -a hero2lte_ref/. target
umount hero2lte_ref

if false
then
	rm target/app
	cp -r "$SRCDIR/app" target/
	cp -r "$SRCDIR/bin/mcDriverDaemon" target/bin/
	cp -r "$SRCDIR/lib" target/
	cp -r "$SRCDIR/lib64" target/
fi

rm -r target/etc/nxp
cp -r "$SRCDIR/etc/nxp" target/etc/
cp -r "$SRCDIR/etc/mixer_paths_0.xml" target/etc
cp -r "$SRCDIR/etc/audio_effects.xml" target/etc
cp -r "$SRCDIR/etc/thermal_info_config.json" target/etc

sed -i 's/hero2lte/gracerlte/g' target/build.prop
sed -i 's/hero2lte/gracerlte/g' target/odm/etc/build.prop
sed -i 's/G935F/N935F/g' target/build.prop
sed -i 's/G935F/N935F/g' target/odm/etc/build.prop

mksquashfs target vendor_gracerlte.img
cp vendor_gracerlte.img $SRCDIR
cd $SRCDIR
rm -r "$WORKDIR"
