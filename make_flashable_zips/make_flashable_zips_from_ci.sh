set -xe
srcdir=$(realpath $(dirname $0))
workdir=$(mktemp -d)
outputdir=$(realpath $(pwd))/output_ci
cd "$workdir"
rm -rf "$outputdir"
mkdir "$outputdir"

for model in herolte hero2lte
do
	rm -rf *

	wget https://gitlab.com/ubports/porting/community-ports/android11/samsung-galaxy-s7/samsung-exynos8890/-/jobs/artifacts/main/raw/out/boot.img?job=devel-flashable-${model} -O boot.img
	wget https://gitlab.com/ubports/porting/community-ports/android11/samsung-galaxy-s7/samsung-exynos8890/-/jobs/artifacts/main/raw/out/recovery.img?job=devel-flashable-${model} -O recovery.img
	#wget https://gitlab.com/ubports/porting/community-ports/android11/samsung-galaxy-s7/samsung-exynos8890/-/jobs/artifacts/main/raw/out/system.img?job=devel-flashable-${model} -O system.simg
	wget https://gitlab.com/ubports/porting/community-ports/android11/samsung-galaxy-s7/samsung-exynos8890/-/jobs/artifacts/main/raw/out/ubuntu.img?job=devel-flashable-${model} -O system.img

	#simg2img system.simg system.img

	mkdir -p META-INF/com/google/android
	cp "$srcdir"/template/META-INF/com/google/android/* META-INF/com/google/android/
	sed -i "/#!\/sbin\/sh/a MODEL=$model" META-INF/com/google/android/update-binary
	date=$(date +%Y-%m-%d)
	zip -r -y -9 "$outputdir"/${model}-${date}.zip META-INF system.img boot.img
	cp "$outputdir"/${model}-${date}.zip "$outputdir"/${model}-${date}-with-recovery.zip
	zip -r -y -9 "$outputdir"/${model}-${date}-with-recovery.zip recovery.img
done

cd ../
rm -r "$workdir"
