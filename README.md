### Credits
https://github.com/8890q/ for LineageOS 18.1 device tree, kernel, hardware support, blobs

https://forum.xda-developers.com/t/treble-aosp-g930x-g935x-project_pizza-trebleport-v2-0.3956076/ for libsensor blobs

https://github.com/NotKit for giving me very helpful hints about ubports/halium specifics

these awesome people gave me useful pointers for https://github.com/Kethen/herolte_treble to come to fruition, and is used in this port:

https://github.com/ivanmeler

https://github.com/ExpressLuke

https://github.com/00p513-dev

### Pending merge requests
- audio routing on focal https://gitlab.com/ubports/development/core/packaging/pulseaudio-modules-droid/-/merge_requests/4

### Currently Known Issues
- focal hotspot toggle is currently in a finicky state, but nmcli/nmtui is working
- starting ap mode (hotspot) after using WPA-PSK-SHA256 in sta mode, or just starting ap mode (hotspot) with WPA-PSK-SHA256, the wifi chip gets into a very inconsistent state until a reboot (broken ap beacons, broken scanning)
	- it is now default disabled
	- if you wish to use ieee80211w/pmf/WPA-PSK-SHA256 on a connection, do `sudo nmcli con mod <connection name> 802-11-wireless-security.pmf required`
- focal NetworkManager + wpa_supplicant stopped triggering periodic re-scan nor handle cfg80211_disconnected, a work-around event handler is currently used to handle cfg80211_disconnected
	- driver triggers cfg80211_disconnected when wifi chip pcie goes down unexpectedly during deep sleep (android style short wake/suspend loop)
	- when cfg80211_disconnected is triggered on the driver side, wifi would stop working until a radio restart from userspace
	- some how reason 32771 is presented to iw on nl80211 during cfg80211_disconnected, but reason 1 ("Unspecified") was issued on the driver
	- cfg80211_disconnected might have never been triggered on xenial due to working periodic re-scan on NetworkManager
- while bluebinder + 3.18 bt stack has issues, bluetooth seems to work with the 4.2 bluetooh stack + hciattach bcm43xx with the help of a few workarounds
	- it might be worth to one day debug why bluebinder is not happy with the generic bcm bt hal from aosp
- swlan0 is disabled to not confuse NetworkManager, but that means no wifi tethering while wifi is connected, wlan0 is used to do both
- fingetprint sensor should work, but only tested on /dev/vfsspi(viper), not /dev/esfp0(egis), I don't have a s7 with egis fingerprint sensor to test with

### Merge requests that were merged
- network manager WPA-PSK-SHA256 workaround https://gitlab.com/ubports/development/core/packaging/network-manager/-/merge_requests/9
- focal hwc screen size issue https://gitlab.com/ubports/development/core/hybris-support/mir-android2-platform/-/merge_requests/11
- Color/Pixel format for hardware video decoding https://github.com/ubports/gst-plugins-bad-packaging/pull/4
- halium-generic-adaptation-build-tools https://gitlab.com/ubports/porting/community-ports/halium-generic-adaptation-build-tools/-/merge_requests/2
- audio routing with pulse https://github.com/ubports/pulseaudio-modules-droid-30/pull/1

### Merge requests that were worked around
- Sensorfw lightsensor https://gitlab.com/ubports/development/core/packaging/sensorfw/-/merge_requests/8

	a binary patch is applied on /vendor/lib64/sensors.sensorhub.so for now, while an alternative fix could likely be applied on android_hardware_samsung/hidl/sensors/1.0/Sensors.cpp; ootb type 65598 is used for lightsensor, type 5 is used for "uncalibrated lightsensor", at least according to symbols available in the vendor blob

### Changes made to recovery
- https://github.com/Kethen/halium_bootable_recovery/tree/halium-11.0-s7
