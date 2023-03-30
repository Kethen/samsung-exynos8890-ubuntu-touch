### Mounting

In decreasing priority, /userdata is mounted from the following loop/block devices
- `/dev/disk/by-partlabel/UT_USERDATA_SD`, ie. a partition with label `UT_USERDATA_SD` on sdcard, not supported by ubport installer/OTA
- `/dev/sda18` on heroxlte, `/dev/sda23` on gracerlte, supported by ubport installer/OTA

In decreasing priority, / is mounted from the following loop/block devices
- `(userdata)/rootfs.img`, not supported by ubport installer/OTA
- `/dev/disk/by-partlabel/UT_SYSTEM_SD`, ie. a partition with label `UT_SYSTEM_SD` on sdcard, not supported by ubport installer/OTA
- `/dev/sda14` on heroxlte, `/dev/sda16` on gracerlte, supported by ubport installer/OTA

With `(userdata)/rootfs.img` and `UT_*_SD` one can perform dual booting shenanigans, but that is in no way supported and OTA will not work.

### Power saving

Currently when the screen is on, aidl powerhal on the halium vendor is instructed to enable `SUSTAINED_PERFORMANCE` + `EXPENSIVE_RENDERING`, while it enables `LOW_POWER` when the screen is off. Clock speeds are raised during that combo to improve responsiveness, and the scheduler will have access to all 4 big cores during instead of 2 in `LOW_POWER` mode.

To always stay in `LOW_POWER` mode, create an empty file at `/home/phablet/.config/power_saving`, one can do that in terminal with `touch /home/phablet/.config/power_saving`. The change is applied the next screen wake.

Slightly dangerous, but advanced users can also adjust power hints at `/home/phablet/.config/powerhint.json` then reboot.

Optionally network power saving can be enabled, which only allows internet to be on for 30 seconds every 2 minutes when screen is off. It can detect whether hotspot is on reliably, but it cannot tell whether any applications need active background internet connection without a proper wakelock like interface on ut itself.

To enable network power saving, create an empty file at `/home/phablet/.config/network_power_saving`, one can do that in terminal with `touch /home/phablet/.config/network_power_saving`. The change is applied the next screen off.

### Anti Flicker

On heroxlte, Ivan included https://forum.xda-developers.com/t/kernel-g935-amoled-pwm-flicker-free.3517739/ into his kernel, which is in turn used as a base for the ubuntu touch kernel. To enable anti flicker/flicker free, create an empty file at `/home/phablet/.config/anti_flicker`, one can do that in terminal with `touch /home/phablet/.config/anti_flicker`. The change is applied the next screen off.

This technically works on gracerlte, but it is disabled due to the lack of testing and panel difference.

### Charging limit

On heroxlte, Ivan included a way to limit charging through sysfs. To limit charging, create a file with the percentage limit 61-94 at `/home/phablet/.config/limit_charging` then reboot, one can do that in terminal with `echo 70 > /home/phablet/.config/limit_charging; sudo reboot`. This works even during offline charging.

### Call echo

Some heroxlte are known for having echo on calls (the other side hears themselves). It is due to the lack of reverse engineered in-modem-ish noise canceling along with cross wired top and bottom microphone on some devices. There is likely not much you can do if you have call echo on LineageOS besides hoping one day the noise canceling mechanism is reverse engineered. But if you want to attempt mitigating it through changing mixer paths, you can change it at `/home/phablet/.config/samsung_mixer_paths_0_override.xml ` then reboot.

### Enable swap file

Currently zswap is enabled by default. If a swap file is also needed to have even more applications in the background, swapfile at `/userdata/SWAP.img` is auto mounted during boot.

This will never be the default since the usage of swap file could rapidly degrade flash storage lifespan. Do that at your own risk.

```
# allocating 2GiB of swap
sudo fallocate /userdata/SWAP.img -l 2G
sudo chmod 600 /userdata/SWAP.img
sudo mkswap /userdata/SWAP.img
sudo reboot
```

### Smoother UI?

I have not been able to have partial updates on mir without screen tearing, but you can tweak that on your own install https://docs.ubports.com/en/latest/porting/configure_test_fix/device_info/Mir.html at `/etc/deviceinfo/devices/<codename>.yaml`
