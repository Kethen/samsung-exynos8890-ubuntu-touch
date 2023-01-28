# because xenial mir server driver do not support forcing hwc2

# clear all mounts
while [ -n "$(mount | grep hwcomposer.exynos5.so)" ]
do
	umount /vendor/lib64/hw/hwcomposer.exynos5.so
done

# wait till /vendor/lib64/hw/hwcomposer.exynos5.so is loaded by hwc2
while [ -z "$(lsof /vendor/lib64/hw/hwcomposer.exynos5.so)" ]
do
	echo waiting for hwc2 to load /vendor/lib64/hw/hwcomposer.exynos5.so
	sleep 0.1
done

mount -o bind /dev/null /vendor/lib64/hw/hwcomposer.exynos5.so
