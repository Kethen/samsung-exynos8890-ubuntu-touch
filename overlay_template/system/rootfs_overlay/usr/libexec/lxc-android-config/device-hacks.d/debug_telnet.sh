/usr/bin/bash /usr/libexec/lxc-android-config/device-hacks.d/usb-tethering.sh &

run_telnet () {
	while true
	do
		/usr/sbin/busybox-armv8l telnetd -F -p 9999 -l /usr/bin/bash
	done
}

run_telnet &

run_debug () {
	echo 120 > /proc/sys/kernel/hung_task_timeout_secs
	sleep 360
	dmesg > /userdata/dmesg
	journalctl -b > /userdata/journal
	sync
	#reboot -f recovery
}

run_debug &
