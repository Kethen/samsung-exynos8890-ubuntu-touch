zramctl /dev/zram0 -s 2147483648
mkswap /dev/zram0
swapon /dev/zram0