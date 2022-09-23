#!/bin/bash

if [ "$1" == "charging" ]
then
	echo 10 > /sys/power/autosleep_delay
fi

if [ "$1" == "discharging" ]
then
	echo 2 > /sys/power/autosleep_delay
fi
