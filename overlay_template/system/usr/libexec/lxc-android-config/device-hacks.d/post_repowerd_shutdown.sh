echo making pre-shutdown power profile changes > /dev/kmsg
echo 1 > /sys/devices/system/cpu/cpu0/cpufreq/interactive/io_is_busy
echo 1 > /sys/devices/system/cpu/cpu4/cpufreq/interactive/io_is_busy
echo off > /sys/power/autosleep
