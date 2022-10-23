#!/bin/bash

if [ "$1" == "charging" ]
then
	echo 10 > /sys/power/autosleep_delay
	echo 25 > /sys/power/autosleep_enter_delay
fi

if [ "$1" == "discharging" ]
then
	echo 1 > /sys/power/autosleep_delay
	echo 5 > /sys/power/autosleep_enter_delay
fi
