1)
sudo nano /boot/firmware/config.txt
or /boot/config.txt on older OS

Write'
dtoverlay=dwc2
'
2)
sudo nano /etc/modules

Write'
dwc2
libcomposite
'

3)
reboot

4)
Create new bash script

sudo nano /usr/local/bin/usb_gadget_setup.sh

Copy data from the sh file from scripts folder
Run the script
sudo /usr/local/bin/usb_gadget_setup.sh

5)
Inside /dev there should be now 2 hidg0 and higd1

6)
Install evdev

sudo apt install python3-evdev

7)
