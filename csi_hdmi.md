cd b2b
tam znajdziesz plik

cat << 'EOF' > 1080p30_edid.txt
00ffffffffffff005262888800888888
1c150103800000780aEE91A3544C9926
0F505400000001010101010101010101
010101010101011D8018711C1620582C
2500C48E2100009E000000FC00546F73
686962612D4832430A20000000FD0032
3D0F2E0F000A20202020202000000010
00000000000000000000000000000185
020321434F041303021211012021223F
40830F000066030C00300080E3007F8C
0AD08A20E02D10103E9600C48E210000
188C0AD08A20E02D10103E9600138E21
0000188C0AA01451F01681204006E044
00009800000000000000000000000000
00000000000000000000000000000000
0000000000000000000000000000001E
EOF

load 1080p30 edid it into a /dev/video0

sudo v4l2-ctl -d /dev/video0 --set-edid=file=1080p30_edid.txt --fix-edid-checksums


Step 2: Manually Tame the Laptop (Crucial)
Before we lock the signal on the Pi, we must force the laptop to behave.

Keep the HDMI plugged in.
Go to your laptop's display settings.
Select the secondary screen (the capture card).
Set the resolution to 1920x1080.
Find the Refresh Rate setting and explicitly click 30Hz (or 24Hz if 30 is missing). If it is stuck on 60Hz, the Pi will crash when we try to view it.

Query and lock signal
Query
v4l2-ctl -d /dev/video0 --query-dv-timings
(You want to see Active width: 1920 and Active height: 1080, with a Pixelclock around 74,250,000 Hz).

Lock
sudo v4l2-ctl -d /dev/video0 --set-dv-bt-timings query

View:
RV24 is vlc version of RGB3 (RGB raw 3 byte output)
vlc v4l2:///dev/video0:chroma=RV24:width=1920:height=1080 --fullscreen --no-qt-fs-controller --no-osd --no-video-title-show