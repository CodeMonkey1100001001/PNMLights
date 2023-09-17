print("raw_video_player_zig_zag_20220705.2033.py")
#ffmpeg -y -i  /tmp/misc/testpattern001.AVI -f rawvideo -vf scale=8:8 -vsync vfr -pix_fmt rgb24 ./testpattern.raw
# TODOs
# add a config.txt
# add file.cfg instead
#
import time
import board
from rainbowio import colorwheel
import neopixel

# fileName = "grid_test_8x8_checker.ppm"
fileName="checker.raw"
fileName="grid_ninja.raw"
#fileName="grid_testpattern.raw"
#fileName = "grid_test_flame.raw"
#fileName = "/patterns/grid_test.raw"
#fileName = "/grid_test.raw"
#fileName = "grid_zig_zag_test.raw"
fileName = "grid_test16x16.raw"
fileName = "testpattern.raw"


# ZigZag and Frame Rate
disableZigZag = False
frameRate = 0.0001 #1/30 # 1/30 = 30fps

# hardware configue - must be evenlydivisible by 2
pixel_pin = board.A3
pixel_width = 16
pixel_height = 16
num_pixels = 16*16


#Init pixels
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)

#make a buffer to hold pixels if it needs to be reversed
theReversedLine = bytearray([0] * pixel_width * pixel_height * 3)
#print("theReversedLine",theReversedLine)

def playPattern(frameRate,theIncomingLine):
    global strip_numPixels
    global np
    #print("incomingline",theIncomingLine)
    #speed=int(theIncomingLine[0:2],16)
    #print("speed",speed/1000)

    theLineLen = int(len(theIncomingLine)/3)
    #print("theLineLen",theLineLen)
    for i in range(0,theLineLen):
        pos = (i * 3 )
        r = theIncomingLine[pos+0]
        g = theIncomingLine[pos+1]
        b = theIncomingLine[pos+2]
        pixels[i] = (r,g,b)
    pixels.show()
    time.sleep(frameRate)
    #time.sleep(0.530)


# main  ##################################

print("Playing fileName",fileName)
fileLen = 0
with open(fileName,"rb") as fp:
    aLine = fp.read(1)
    while aLine:
        fileLen += 1
        aLine = fp.read(1)
print("fileLen",fileLen)
fileFrame = int(fileLen / (pixel_height * pixel_width * 3))
print("fileFrame",fileFrame)
while True:
    #print("file open"+fileName)
    with open(fileName,"rb") as fp:
        #print("file")
        for lop in range(0,fileFrame): # 3 frames
            #print("=============FRAME===========",lop)
            #theReversedLine = bytearray(pixel_width*pixel_height*3)
            #print("pixel_height",pixel_height)
            for y in range(0,pixel_height):
                #print("row",y)
                aLine = fp.read(pixel_width*3)

                for x in range(0,pixel_width):

                    if disableZigZag or (y % 2) == 0:  # normal Direction
                        rPos = (pixel_width * 3 * y) + pixel_width * 3 - 3 * x -3
                        gPos = (pixel_width * 3 * y) + pixel_width * 3 - 3 * x -2
                        bPos = (pixel_width * 3 * y) + pixel_width * 3 - 3 * x  -1
                    else:
                        rPos = (pixel_width * 3 * y) + 3 * x + 0
                        gPos = (pixel_width * 3 * y) + 3 * x + 1
                        bPos = (pixel_width * 3 * y) + 3 * x + 2

                    theReversedLine[rPos]=aLine[x * 3 + 0] # r
                    theReversedLine[gPos]=aLine[x * 3 + 1] # g
                    theReversedLine[bPos]=aLine[x * 3 + 2] # b
            playPattern(frameRate,theReversedLine)
            #print("frame",y)
