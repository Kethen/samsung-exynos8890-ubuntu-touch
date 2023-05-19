# waydroid gets stuck if gnss is not registered properly

get_gnss_pid () {
	ps -ef | grep -v grep | grep 'vendor.samsung.hardware.gnss@1.0-service' | awk '{print $2}'
}

get_gnss_status () {
	if [ -z "$(android_shell.sh lshal | grep 'android.hardware.gnss@1.1::IGnss/default' | grep DM)" ]
	then
		echo down
	else
		echo up
	fi
}

echo gnss started at $(get_gnss_pid)

echo checking if gnss service is registered properly

cnt=0
while [ "$(get_gnss_status)" == "down" ] && [ $cnt -lt 120 ]
do
	gnss_pid=$(get_gnss_pid)
	echo \#$cnt try
	if [ -n "$gnss_pid" ]
	then
		echo killing gnss to trigger a restart
		kill $gnss_pid
		setprop ctl.start sec_gnss_service
	else
		echo gnss did not start at all
	fi
	cnt=$((cnt+1))
	sleep 0.5
done

echo gnss is $(get_gnss_status) after $cnt restart\(s\)
