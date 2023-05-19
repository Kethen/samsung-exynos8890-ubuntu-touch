if [ -d /home/phablet/.local/share/waydroid_local_image ]
then
	mount -o bind /home/phablet/.local/share/waydroid_local_image /usr/share/waydroid-extra/images
fi
