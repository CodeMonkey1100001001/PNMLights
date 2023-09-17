# Read a P3 file from the serial port and display on NeoPixel strand. Usefull for an
# X * Y array of neopixels
#ppm6_binary.py
print("I Am P3FromSerial.py")
print("Version 20230912.1019")
#stty -F /dev/ttyACM0 300 raw ; cat </tmp/misc/P3Ascii_rainbow.ppm | tr '\n' '\r' >/dev/ttyACM0 

import time
import board
from rainbowio import colorwheel
import neopixel

pixel_pin = board.A3
num_pixels = 16*16
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)
disableZigZag = False



def playPattern(theIncomingLine):
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

# fileName = "grid_test_8x8_checker.ppm"
#fileName="P3Ascii.ppm"
#print("fileName",fileName)
while True:
    fileType = input()
    comment  = input()
    xandy    = input().split()
    depth    = input()
    frameRate = 30/1000

    print("fileType",fileType)
    print("comment",comment)
    print("x and y",xandy)
    print("depth",depth)
        

    if (fileType.startswith("P3")):
        print("P3 File")
        xDimension = int(xandy[0])
        yDimension = int(xandy[1])
        print("x=",xDimension,"y=",yDimension)
        theBuffer = bytearray([0] * xDimension * yDimension * 3)
        
        # now read the rest of the file knowing the X,Y
        pixelPointer = 0
        for y in range(0,yDimension):
            for x in range(0,xDimension):
                r = int(input())
                g = int(input())
                b = int(input())

                if disableZigZag or (y % 2) == 0:  # normal Direction
                    rPos = (xDimension * 3 * y) + 3 * x + 0
                    gPos = (xDimension * 3 * y) + 3 * x + 1
                    bPos = (xDimension * 3 * y) + 3 * x + 2
                else:
                    rPos = (xDimension * 3 * y) + xDimension * 3 - 3 * x -3
                    gPos = (xDimension * 3 * y) + xDimension * 3 - 3 * x -2 
                    bPos = (xDimension * 3 * y) + xDimension *3 - 3 * x  -1
                    
                theBuffer[rPos] = r
                theBuffer[gPos] = g
                theBuffer[bPos] = b
                print("RGBPOS=",rPos,gPos,bPos)
        playPattern(theBuffer)
        print("Done")
while True:
    pass
    
