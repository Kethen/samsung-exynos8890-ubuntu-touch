#!/bin/bash

####
# Default profile
USB_IDVENDOR=0FCE
USB_IDPRODUCT=7169
USB_IPRODUCT="Unknown"
USB_ISERIAL="Unknown"
USB_IMANUFACTURER="GNU/Linux Device"
USB_IFACE="rndis0"

####
# Override profile
if [ -f /etc/default/hybris-device ]; then
    source /etc/default/hybris-device
fi

ANDROID_USB=/sys/class/android_usb/android0
USB_FUNCTIONS=rndis
LOCAL_IP=10.15.19.82
GADGET_DIR=/sys/kernel/config/usb_gadget

write() {
    echo -n "$2" > "$1"
}

# This sets up the USB with whatever USB_FUNCTIONS are set to via configfs
usb_setup_configfs() {
    G_USB_ISERIAL=$GADGET_DIR/g1/strings/0x409/serialnumber

    mkdir $GADGET_DIR/g1
    write $GADGET_DIR/g1/idVendor                   "0x$USB_IDVENDOR"
    write $GADGET_DIR/g1/idProduct                  "0x$USB_IDPRODUCT"
    mkdir $GADGET_DIR/g1/strings/0x409
    write $GADGET_DIR/g1/strings/0x409/serialnumber "$USB_ISERIAL"
    write $GADGET_DIR/g1/strings/0x409/manufacturer "$USB_IMANUFACTURER"
    write $GADGET_DIR/g1/strings/0x409/product      "$USB_IPRODUCT"

    if echo $USB_FUNCTIONS | grep -q "rndis"; then
        mkdir $GADGET_DIR/g1/functions/rndis.usb0
        mkdir $GADGET_DIR/g1/functions/rndis_bam.rndis
    fi
    echo $USB_FUNCTIONS | grep -q "mass_storage" && mkdir $GADGET_DIR/g1/functions/storage.0

    mkdir $GADGET_DIR/g1/configs/c.1
    mkdir $GADGET_DIR/g1/configs/c.1/strings/0x409
    write $GADGET_DIR/g1/configs/c.1/strings/0x409/configuration "$USB_FUNCTIONS"

    if echo $USB_FUNCTIONS | grep -q "rndis"; then
        ln -s $GADGET_DIR/g1/functions/rndis.usb0 $GADGET_DIR/g1/configs/c.1
        ln -s $GADGET_DIR/g1/functions/rndis_bam.rndis $GADGET_DIR/g1/configs/c.1
    fi
    echo $USB_FUNCTIONS | grep -q "mass_storage" && ln -s $GADGET_DIR/g1/functions/storage.0 $GADGET_DIR/g1/configs/c.1

    ls /sys/class/udc > $GADGET_DIR/g1/UDC
}

# This sets up the USB with whatever USB_FUNCTIONS are set to via android_usb
usb_setup_android_usb() {
    G_USB_ISERIAL=$ANDROID_USB/iSerial
    write $ANDROID_USB/enable          0
    write $ANDROID_USB/functions       ""
    write $ANDROID_USB/enable          1
    #usleep 500000 # 0.5 delay to attempt to remove rndis function
    sleep 1
    write $ANDROID_USB/enable          0
    write $ANDROID_USB/idVendor        $USB_IDVENDOR
    write $ANDROID_USB/idProduct       $USB_IDPRODUCT
    write $ANDROID_USB/iManufacturer   "$USB_IMANUFACTURER"
    write $ANDROID_USB/iProduct        "$USB_IPRODUCT"
    write $ANDROID_USB/iSerial         "$USB_ISERIAL"
    write $ANDROID_USB/functions       $USB_FUNCTIONS
    write $ANDROID_USB/enable          1
}

# This determines which USB setup method is going to be used
usb_setup() {
    mount -t configfs none /sys/kernel/config || true

    if [ -d $ANDROID_USB ]; then
        usb_setup_android_usb
    elif [ -d $GADGET_DIR ]; then
        usb_setup_configfs
    fi
}

usb_info() {
    sleep 1
    write $G_USB_ISERIAL "$1"
    echo "$1" >> /var/log/usb_info.log
}

ip_setup() {
    local candidate

    if [ -n "$USB_IFACE" ]; then
        while [ -z "$(ip link list | grep ${USB_IFACE}':')" ]
        do
        	sleep 1
        done
        ip link set dev "$USB_IFACE" up
    fi
    
    if [ -z "$USB_IFACE" ]; then
        # Prioritise usb0 over rndis0. On some devices (e.g. Sony Xperia X),
        # both would show up but only usb0 is usable. If, on some device, the
        # opposite happens, then I don't know what to do.
        for candidate in usb0 rndis0; do
            if ip link set dev "$candidate" up; then
                USB_IFACE="$candidate"
                break
            fi
        done
    fi

    if [ -z "$USB_IFACE" ]; then
        usb_info "could not setup USB tethering!"
        return 1
    fi

    ip address add "${LOCAL_IP}/24" dev "$USB_IFACE"

    usb_info "$USB_IMANUFACTURER on $USB_IFACE $LOCAL_IP"
}

dhcpd_start() {
	mkdir -p /run/hybris-usb
	touch /run/hybris-usb/dhcpd4.leases
	/usr/sbin/dhcpd -4 -q \
        -cf /etc/hybris-usb/dhcpd.conf \
        -pf /run/hybris-usb/dhcpd4.pid \
        -lf /run/hybris-usb/dhcpd4.leases \
        "$USB_IFACE"
}

usb_setup
ip_setup
ip addr list > /userdata/ip_addr
dhcpd_start
ss -tuapn > /userdata/ss
sync

exit $?
