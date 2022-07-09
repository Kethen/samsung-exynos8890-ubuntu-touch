### Currently Known Issues
- audio port switching seems broken with pulseaudio-modules-droid, while microphone is broken with pulseaudio-modules-droid-jb2q, so audio is kinda there but not ready
- light sensor should be working but auto brightness does not work
- video player crashes when presented with omx pixels from samsung, perhaps I should just build omx soft codecs to make up for that
- swlan0 is disabled to not confuse NetworkManager, but that means no wifi tethering
- sdcard support is missing
- fingetprint sensor cannot enroll, something about trustzone/mobicore not working
- NetworkManager sometimes starts before mac address is loaded from /efs, deciding on a fix

### TODO
- add hero2lte port
