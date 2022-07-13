### Currently Known Issues
- bluetooth seems to work best with the 4.2 bluetooh stack, unlike with bluebinder and 3.18 device can connect and communite correctly, however:
	- full power off has to be disabled for it to play well with the uart hci, hopefully the wifi chip itself takes the power down command well
	- hciattach can't set a macaddress at all with this chip, so the macaddress from /efs cannot be applied, while the chip has a built-in mac address
- light sensor should be working but auto brightness does not work
- video player crashes when presented with omx pixels from samsung, perhaps I need to make omx use soft decoders for now
- swlan0 is disabled to not confuse NetworkManager, but that means no wifi tethering while wifi is connected, wlan0 is used to do both
- sdcard support is missing
- fingetprint sensor cannot enroll, something about trustzone/mobicore not working

### TODO
- add hero2lte port
