# because xenial mir server driver do not support forcing hwc2
while [ ! -e /dev/socket/property_service ]; do sleep 0.1; done
while [ -z "$(getprop ro.build.version.sdk)" ]; do sleep 0.1; done
while [ -z "$(ps -ef | grep android.hardware.graphics.composer@2.1-service)" ]; do sleep 0.1; done
sleep 0.5
if [ -z "$(mount | grep hwcomposer.exynos5.so)" ]
then
	mount -o bind /dev/null /vendor/lib64/hw/hwcomposer.exynos5.so
fi
