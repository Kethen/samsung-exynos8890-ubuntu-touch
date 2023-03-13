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

(
	cd target
	cat $SRCDIR/hero2lte_remove_list | while read -r LINE
	do
		rm $LINE
	done
)

cp -r "$SRCDIR/etc" target/
cp -r "$SRCDIR/app" target/
cp -r "$SRCDIR/lib" target/
cp -r "$SRCDIR/lib64" target/
cp -r "$SRCDIR/bin" target/

sed -i 's/hero2lte/gracerlte/g' target/build.prop
sed -i 's/hero2lte/gracerlte/g' target/odm/etc/build.prop
sed -i 's/G935F/N935F/g' target/build.prop
sed -i 's/G935F/N935F/g' target/odm/etc/build.prop

mksquashfs target vendor_gracerlte.img
cp vendor_gracerlte.img $SRCDIR
cd $SRCDIR
rm -r "$WORKDIR"
