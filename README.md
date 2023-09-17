# PNMLights
Use PNM images with Neopixel or other individually addressable RGB(w) LEDs.

# convert a animated gif to raw video to be used by
# CPNPRawVideoPlayer.py
ffmpeg -y -i  /tmp/misc/color.gif -f rawvideo -vf scale=16:16 -vsync vfr -pix_fmt rgb24 ./testpattern.raw
