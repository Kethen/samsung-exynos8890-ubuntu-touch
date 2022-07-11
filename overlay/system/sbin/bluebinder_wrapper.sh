#!/bin/bash
rm -f /tmp/bluebinder_wrapper_fifo
mkfifo /tmp/bluebinder_wrapper_fifo

while true
do
	/usr/sbin/bluebinder 2> /tmp/bluebinder_wrapper_fifo &
	BLUEBINDER_PID=$!
	echo started bluebinder on pid $BLUEBINDER_PID
	cat /tmp/bluebinder_wrapper_fifo | while read -r LINE
	do
		echo $LINE
		if [ "$LINE" == "Turning bluetooth off" ] || [ "$LINE" == "Writing packet from HAL to vhci device failed: No such device or address" ]
		then
			echo killing bluebinder on pid $BLUEBINDER_PID
			kill $BLUEBINDER_PID
			sleep 5
			break
		fi
	done
done
