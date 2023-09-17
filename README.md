# PNMLights

This project is about leveraging open standards for images and videos to control individually addressable RGB(w) LEDs. (eg. NeoPixels, WS2812*) 

# Images
For images the Portable aNy Map (PNM) file format is used.

# Video
For video a very generic raw video format that can be output by ffmpeg is used.

Examples:

To convert a animated gif to raw video to be used by CPNPRawVideoPlayer.py
```
ffmpeg -y -i  inputanim.gif -f rawvideo -vf scale=16:16 -vsync vfr -pix_fmt rgb24 ./processedvideo.raw
ffmpeg -y -i  inputanim.mp4 -f rawvideo -vf scale=16:16 -vsync vfr -pix_fmt rgb24 ./processedvideo.raw
```

The .raw files is stored on the virtual storage of a device.

# WIP
This is a work in progress.
