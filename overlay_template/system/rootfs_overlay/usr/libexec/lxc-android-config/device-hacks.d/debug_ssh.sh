/usr/bin/usb-tethering &
systemctl start ssh
echo 30 > /proc/sys/kernel/hung_task_timeout_secs
sleep 60
dmesg > /userdata/dmesg
journalctl -b > /userdata/journal
sync
reboot -f recovery
