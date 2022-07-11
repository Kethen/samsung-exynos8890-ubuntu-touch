### Currently Known Issues
- light sensor should be working but auto brightness does not work
- video player crashes when presented with omx pixels from samsung, perhaps I need to make omx use soft decoders for now
- swlan0 is disabled to not confuse NetworkManager, but that means no wifi tethering while wifi is connected, wlan0 is used to do both
- sdcard support is missing
- fingetprint sensor cannot enroll, something about trustzone/mobicore not working
- NetworkManager sometimes starts before mac address is loaded from /efs, deciding on a fix

### TODO
- add hero2lte port
