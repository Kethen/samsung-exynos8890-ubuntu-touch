echo registering the pid namespace of lxc container to the fingerprint sensor driver

if [ -e /dev/vfsspi ]
then
	echo /dev/vfsspi detected, setting android init pid to driver
	/usr/sbin/vfsspi_fix $(lxc-info -n android | grep PID | awk '{print $2}')
fi

if [ -e /dev/esfp0 ]
then
	echo /dev/esfp0 detected, setting android init pid to driver
	/usr/sbin/esfp0_fix $(lxc-info -n android | grep PID | awk '{print $2}')
fi

echo starting fingerprint hal
setprop ctl.start vendor.fps_hal
