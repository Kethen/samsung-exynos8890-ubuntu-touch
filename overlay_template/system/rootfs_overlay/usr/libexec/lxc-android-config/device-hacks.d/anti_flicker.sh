if [ -e /home/phablet/.config/anti_flicker ] && [ "$(getprop ro.product.device)" != "gracerlte" ]
then
	echo 1 > /sys/class/lcd/panel/smart_on
fi
