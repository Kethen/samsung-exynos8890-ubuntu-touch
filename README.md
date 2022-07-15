### Currently Known Issues
- bluetooth seems to work best with the 4.2 bluetooh stack, unlike with bluebinder and 3.18 device can connect and communite correctly, however:
	- full power off has to be disabled for it to play well with the uart hci, hopefully the wifi chip itself takes the power down command well
	- hciattach can't set a macaddress at all with this chip, so the macaddress from /efs cannot be applied, while the chip has a built-in mac address
- built-in video player can't play videos (media-hub-server crashes) and I don't really know why at this point
- swlan0 is disabled to not confuse NetworkManager, but that means no wifi tethering while wifi is connected, wlan0 is used to do both
- fingetprint sensor should work, but only tested on /dev/vfsspi(viper), not /dev/esfp0(egis), I don't have a s7 with egis fingerprint sensor to test with

### TODO
- move android_overlay and vendor_overlay into /opt/halium-overlay
- look into ubports recovery 
- add hero2lte port
