#!/bin/bash

/tmp/usb_property_watcher/setprop "$1" "$2"
if [ "$1" == "persist.sys.usb.config" ]
then
	start mtp-state
fi
