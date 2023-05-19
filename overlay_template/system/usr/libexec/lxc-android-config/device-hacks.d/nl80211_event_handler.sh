LOG_TO_FILE=false

log () {
	if $LOG_TO_FILE
	then
		echo "$(date): $1" >> /userdata/iw_event_log
		sync
	fi
	echo "$1"
}

log_event () {
	log "event: $1"
}

init_event_handler () {
	if $LOG_TO_FILE
	then
		rm /userdata/iw_event_log
	fi
}

process_event () {
	event="$1"
	if [ -n "$(echo $event | grep wlan0 | grep 'disconnected (by AP) reason: 32771')" ]
	then
		log "hack: restarting wifi on network manager on AP disconnect with reason 32771"
		nmcli radio wifi off
		nmcli radio wifi on
	fi
}

init_event_handler

while read -r LINE
do
	log_event "$LINE"
	process_event "$LINE"
done < <(iw event 2>&1)
