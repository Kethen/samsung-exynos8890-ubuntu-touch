zramctl /dev/zram0 -s 2147483648
mkswap /dev/zram0
swapon -p 32767 /dev/zram0
