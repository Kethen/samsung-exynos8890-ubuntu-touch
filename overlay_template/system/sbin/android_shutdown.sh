#!/bin/bash

kill_process () {
	for pid in $(ps -ef | grep " $1" | grep -v grep | awk '{print $2}')
	do
		kill -s $2 $pid
	done
	for pid in $(ps -ef | grep " $(which $1)" | grep -v grep | awk '{print $2}')
	do
		kill -s $2 $pid
	done
}

echo stopping binder using services
date
stop -n lightdm
stop -n biometryd
stop -n sensorfw
stop -n ofono
stop -n nfcd
stop -n bluebinder
stop -n repowerd
stop -n ubuntu-location-service
stop -n hfd-service

echo kill processes that have issues stopping
date
kill_process hfd-service SIGTERM
kill_process sensorfwd SIGKILL

echo waiting for libhybris to release binders
date
while [ -n "$(lsof -t /dev/hwbinder)" ] || [ -n "$(lsof -t /dev/binder)" ]
do
	echo /dev/hwbinder
	lsof /dev/hwbinder
	echo /dev/binder
	lsof /dev/binder
	sleep 0.1
done

echo stopping android
date
lxc-stop -n android -k


