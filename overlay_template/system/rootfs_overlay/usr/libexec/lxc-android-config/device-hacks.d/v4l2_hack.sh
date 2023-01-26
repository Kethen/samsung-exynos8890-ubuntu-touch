# gst-plugin-scan panics parts of exynos-fimc (exynos camera v4l2 interface)
# page fault happens at v4l_querycap, but null checking does not help
# a cleaner fix would be locating exactly which v4l2 ioctl device has a quacked querycap pointer
# but null checking did not catch it so I'm not sure which one exactly
# here is a temporary fix which just hide offending v4l2 devices from ut userspace

for f in /sys/class/video4linux/video*/name
do
	RES=$(cat $f | grep exynos-fimc-is)
	if [ -n "$RES" ]
	then
		TARGET=$(echo $f | sed -E 's/\/sys\/class\/video4linux\/(video[0-9]+)\/name/\1/')
		rm /dev/$TARGET
	fi
done
