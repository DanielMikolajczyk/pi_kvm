1)
lsusb

Look through the list. You should see something like "MacroSilicon", "USB Video", or "Video Capture". If you see that, the hardware is recognized.

2)
Run the list devices command:
v4l2-ctl --list-devices

Look for the name of your USB adapter (it will likely say "USB Video" or something similar, not "unicam").

Note the very first /dev/videoX number listed directly under it. For USB devices, it often grabs /dev/video0 or /dev/video1.

3)
ffplay /dev/video0 (to check if you see the screen)

4)
"Perfect but resolutions do not match - on laptop i have 1920x1200 - but i know that hdmi to usb have some serious constraints (1920x1080 30p). What should i do?"

Step 1: Switch to "Extend" Mode (Crucial)
If your laptop is currently set to "Duplicate" or "Mirror" the screen, Windows or macOS is trying to force a single compromise resolution on both screens. We need to decouple them.

On Windows: Press Windows Key + P and select Extend.

On Mac: Go to System Settings > Displays, and set the capture card to Stop Mirroring or Use as Separate Display.

Step 2: Force 1080p on the Capture Card
Now that the displays are independent, your laptop screen can stay at its native 1920x1200, while we spoon-feed the USB dongle the exact 1920x1080 signal it craves.

Go into your laptop's display settings.

Select the second monitor (the USB capture card).

Change its specific display resolution to 1920 x 1080.

(Optional but recommended): Check the refresh rate for that display and make sure it is set to 30Hz or 60Hz. (Most budget USB dongles max out at 1080p 30Hz; if you send it 60Hz, it might drop frames or downgrade to 720p automatically).

ffplay -f v4l2 -video_size 1920x1080 -framerate 30 -i /dev/video0 -fflags nobuffer -flags low_delay -framedrop

5)
If colors don't match

Cheap HDMI-to-USB dongles (usually using the MacroSilicon chip) almost always compress 1080p video into MJPEG format because they don't have the USB bandwidth to send raw, uncompressed 1080p video. VLC often defaults to raw video, hence the green screen.

vlc v4l2:///dev/video1:chroma=mjpg:width=1920:height=1080
ffplay -f v4l2 -input_format mjpeg -video_size 1920x1080 -i /dev/video1

6)
No On-Screen Controler in vlc when moving mouse (time, volume etc.)
vlc v4l2:///dev/video1:chroma=mjpg:width=1920:height=1080 --fullscreen --no-qt-fs-controller --no-osd --no-video-title-show

Tools > Preferences
Interference tab
Show controls in fullscreen mode and uncheck it.

7)
It is also good to go to laptop display settings. Mark the 2nd monitor - and change the resolution to 1920x1080 30Hz