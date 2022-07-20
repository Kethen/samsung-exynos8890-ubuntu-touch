srcdir=$(realpath $(dirname $0))
ubports_output=$(realpath $srcdir/../out)
workdir=$(mktemp -d)
outputdir=$(realpath $(pwd))/output
cd "$workdir"

rm -rf "$outputdir"
mkdir "$outputdir"

for model in herolte hero2lte
do
	rm -rf *
	simg2img "$ubports_output"/system_${model}.img system.img
	cp "$ubports_output"/boot_${model}.img boot.img
	mkdir -p META-INF/com/google/android
	cp "$srcdir"/template/META-INF/com/google/android/* META-INF/com/google/android/
	sed -i "/#!\/sbin\/sh/a MODEL=$model" META-INF/com/google/android/update-binary
	zip -r -y -9 "$outputdir"/${model}-$(date +%Y-%m-%d).zip META-INF system.img boot.img
done

cd ../
rm -r "$workdir"
