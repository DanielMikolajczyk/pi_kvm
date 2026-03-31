echo "" > /sys/kernel/config/usb_gadget/pikvm/UDC
rm /sys/kernel/config/usb_gadget/pikvm/configs/c.1/hid.usb0
rm /sys/kernel/config/usb_gadget/pikvm/configs/c.1/hid.usb1
rmdir /sys/kernel/config/usb_gadget/pikvm/functions/hid.usb0
rmdir /sys/kernel/config/usb_gadget/pikvm/functions/hid.usb1
rmdir /sys/kernel/config/usb_gadget/pikvm/configs/c.1/strings/0x409
rmdir /sys/kernel/config/usb_gadget/pikvm/configs/c.1
rmdir /sys/kernel/config/usb_gadget/pikvm/strings/0x409
rmdir /sys/kernel/config/usb_gadget/pikvm
exit
