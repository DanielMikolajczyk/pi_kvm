#!/bin/bash
modprobe libcomposite

cd /sys/kernel/config/usb_gadget/
mkdir -p pikvm3
cd pikvm3

echo 0x1d6b > idVendor
echo 0x0108 > idProduct  # NEW ID to bust the cache!
echo 0x0100 > bcdDevice
echo 0x0200 > bcdUSB

mkdir -p strings/0x409
echo "fedcba9876543210" > strings/0x409/serialnumber
echo "Raspberry Pi" > strings/0x409/manufacturer
echo "Absolute KVM" > strings/0x409/product

mkdir -p configs/c.1/strings/0x409
echo "Config 1" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

# --- DEVICE 1: KEYBOARD (Unchanged) ---
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 8 > functions/hid.usb0/report_length
python3 -c "open('functions/hid.usb0/report_desc', 'wb').write(bytes.fromhex('05010906a101050719e029e71500250175019508810295017508810395057501050819012905910295017503910395067508150025650507190029658100c0'))"
ln -s functions/hid.usb0 configs/c.1/

# --- DEVICE 2: ABSOLUTE MOUSE ---
mkdir -p functions/hid.usb1
echo 2 > functions/hid.usb1/protocol
echo 1 > functions/hid.usb1/subclass
echo 5 > functions/hid.usb1/report_length  # Changed from 4 to 5 bytes
# New Touchscreen/Absolute Mouse Descriptor
python3 -c "open('functions/hid.usb1/report_desc', 'wb').write(bytes.fromhex('05010902a1010901a10005091901290315002501950375018102950175058103050109300931150026ff7f350046ff7f751095028102c0c0'))"
ln -s functions/hid.usb1 configs/c.1/

ls /sys/class/udc > UDC