# master.py # 20220603.2034
import os
import time
import random
import usb_cdc
import board
import sdcardio
import storage
import time
import neopixel

# https://learn.adafruit.com/adafruit-adalogger-featherwing/pinouts
# On Atmel M0, M4, 328p or 32u4 it's on GPIO 10


swVersion = "+AT Commands on CircuitPython v20230919.1925"

serialBuffer = bytearray(512)
serialBufferPointer = 0
serialBufferLen = len(serialBuffer)

incomingCommand = ""

knownCommands = {
    "+ID": "id",
    "+INFO": "info",
    "+CCLK": "cclk",
    "+RAND": "make_rand",
    "+DIR" : "get_dir",
    "+PLAY" : "play_file",
    "?": "help"
}

def play_file(arguments):
    global GLOBAL_fp
    global GLOBAL_frameSize
    global GLOBAL_pixel_width
    global GLOBAL_pixel_height

    print("+INFO: playing file",arguments)

    if GLOBAL_fp != None:
        # close previous file
        GLOBAL_fp.close()
        GLOBAL_fp = None

    if GLOBAL_fp == None:
        print("+INFO: file not open")
        stats = os.stat(arguments)
        fileLen = stats[6]
        print("+INFO: file",arguments,"size=",fileLen)
        GLOBAL_fp = open(arguments,"rb")
        GLOBAL_frameSize = GLOBAL_pixel_height * GLOBAL_pixel_width * 3
        totalFrames = int( fileLen / GLOBAL_frameSize)
        print("+INFO: frames", totalFrames)
    return True


def get_dir(arguments):
    print("arguments",arguments)
    if len(arguments) <1:
        rootPath = "/sd"
    else:
        rootPath = arguments

    # print(os.listdir(rootPath))
    for file in os.listdir(rootPath):
        stats = os.stat(rootPath + "/" + file)
        filesize = stats[6]
        print(file, filesize)
    return True

def doNothing(ignoreme):
    return True


def printSerial(whatToPrint):
    print(whatToPrint, end='\r\n')


def id(arguments):
    global uart, swVersion
    print("+ID: "+swVersion)
    print('+IDOS: ' + str(os.uname()) + "\r\n")
    return True


def help(arguments):
    print("+Known Commands")
    for oneCommand in knownCommands:
        print(oneCommand)


def make_rand(arguments):
    print("+Arguments[" + arguments + "]")
    print(arguments[1:])
    maxValue = getInt(arguments)
    if (maxValue < 0):
        maxValue = 10
        print("+INFO MaxValue invalid using 10")
    print("+MaxValue = " + str(maxValue))
    print("+MinValue = 0")
    print("+Rand = " + str(random.randint(0, maxValue)))
    return True


def info(arguments):
    print("info requested")
    print("Is this the info you want?")
    return True


def cclk(arguments):
    print("+INFO: time requested")
    timeNow = "+" + str(time.monotonic())
    print(timeNow)
    return True


#####################
def hexDumpStr(theStr):
    theStr = str(theStr)
    # print("hexdump_type",type(theStr))
    for character in theStr:
        print(hex(ord(character)), end='')
    print()


def getInt(inStrVal):
    # hexDumpStr(inStrVal)
    retInt = -1
    try:
        retInt = int((inStrVal))
    except:
        retInt = -1
        print("Error converting Int[" + str(inStrVal) + "]")
    return retInt


def serialBufferToString():
    global serialBuffer, serialBufferPointer
    returnValue = ""
    i = 0
    for i in range(0, serialBufferPointer):
        # print("i",i,"=",chr(serialBuffer[i]))
        returnValue += chr(serialBuffer[i])
    # upper case only until = or whitespace or not...whatever
    return returnValue  # returnValue.upper()


def serialBufferFlush():
    global serialBuffer, serialBufferPointer
    i = 0
    while i < len(serialBuffer):
        serialBuffer[i] = 0x00
        i += 1
    serialBufferPointer = 0


def parseIncomingTry(theCommand):
    retV = False
    # retV = parseIncoming(theCommand)  # HERE uncomment to see errors
    # return retV

    try:
        retV = parseIncoming(theCommand)
    except:
        print("Error processing incoming")
        return False
    return retV


def parseIncoming(theCommand):
    global knownCommands
    theCommandUpper = theCommand.upper()
    # print("type_theCommand",type(theCommand),theCommand)
    if (len(theCommand) < 3):
        if theCommandUpper == "AT":
            return True
        return False
    # print ("theCommand["+theCommand+"]")

    aMatch = 0
    doCommand = ""
    arguments = ""

    for i in knownCommands:
        # print("i=",i,"func=",knownCommands[i])
        aMatch = compareCommand(i, theCommandUpper)
        if (aMatch >= 1):
            doCommand = knownCommands[i]
            if (len(i) + 1 >= len(theCommand)):
                arguments = ""
            else:
                arguments = theCommand[len(i) + 3:]
                arguments = arguments.rstrip()
                if (aMatch == 2):
                    arguments = theCommand
            # print("command Match",i,"doCommand",doCommand,"aMatch",aMatch)
    if len(doCommand) > 0:
        globals()[doCommand](arguments)
    else:
        print("ERROR")
        return False

    return True


def compareCommand(needle, haystack):
    # _ underscore is a wildcard for numeric values
    retV = 0
    wildCardMatch = 0
    # print("needle:",needle)
    # print("haystack:",haystack)
    startPos = 2  # ignore the AT and any space
    # print("startPos:",startPos)
    compareLen = len(needle)
    # print("compareLen",compareLen)
    for i in range(0, compareLen):
        # print("i=",i)
        if (i + startPos >= len(haystack)):
            haystackChar = "*"
        else:
            haystackChar = haystack[i + startPos]
        needleChar = needle[i]
        # print("needleChar["+needleChar+"] haystackChar["+haystackChar+"]")
        if (needleChar == haystackChar):
            retV = retV + 1
            # print("hit")
        else:
            # print("hs["+haystack[i+startPos]+"]")
            if (needle[i] == '_' and haystackChar.isdigit()):  # >='0' and haystackChar <='9'):
                retV = retV + 1
                wildCardMatch = 1

    # print("compareLen",compareLen,"retV",retV)
    if (compareLen == retV):
        retV = 1
    else:
        retV = 0

    if (retV == 1) and (wildCardMatch == 1):
        retV = 2

    return retV

def playOneFrame():
    global GLOBAL_fp
    global GLOBAL_frameSize
    global GLOBAL_pixel_height
    global GLOBAL_pixel_width
    aFrame = GLOBAL_fp.read(GLOBAL_frameSize)
    #print("reading",GLOBAL_frameSize,"bytes")
    #zig zag?
    # for i in range(GLOBAL_pixel_height):
    #     if i % 2 == 0:
    #         # flip this line but do it in pairs of 3
    #         for j in range(GLOBAL_pixel_width / 2):
    #             tempValue = aFrame[i*GLOBAL_pixel_height + j ]
    #             aFrame[i*GLOBAL_pixel_height + GLOBAL_pixel_width - j] = tempValue
    playPattern(0.001,aFrame)
    # hexDumpStr(aFrame)
    #print("frame")
    if not aFrame:
        print("+INFO: at the end of the file rewind")
        GLOBAL_fp.seek(0)
        # time.sleep(1)

def playPattern(frameRate,theIncomingLine):
    global strip_numPixels
    global np
    global GLOBAL_pixels
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
        GLOBAL_pixels[i] = (r,g,b)
    GLOBAL_pixels.show()
    time.sleep(frameRate)
    #time.sleep(0.530)


def doOtherStuff(timeNow):
    global tickTime
    global GLOBAL_fp
    if timeNow - tickTime > 60:
        print("+INFO: Tick", timeNow)
        tickTime = timeNow
    # if playing a file do the next frame
    if GLOBAL_fp != None:
        playOneFrame()


# ----------------------------
# Main Code begins here
# ----------------------------
print("+BOOT")
id('')
print("OK")

buffer = ""
serial = usb_cdc.console

oldTime = time.monotonic()
runStart = oldTime
tickTime = oldTime

sd = sdcardio.SDCard(board.SPI(), board.D10)  # apparently the SD Logger board uses D10 as CS)
vfs = storage.VfsFat(sd)
storage.mount(vfs, '/sd')
time.sleep(0.5)

GLOBAL_fp = None
GLOBAL_frameSize = None
GLOBAL_pixel_height = 16
GLOBAL_pixel_width = 16

pixel_pin = board.A3
pixel_width = 16
pixel_height = 16
num_pixels = 16*16


#Init pixels
GLOBAL_pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)



while True:
    now = time.monotonic()
    doOtherStuff(now)
    oldTime = now
    while serial.in_waiting:
        inByte = serial.read(1)
        # print("["+chr(inByte[0])+"]", end='')
        print(chr(inByte[0]), end='')
        serialBuffer[serialBufferPointer] = inByte[0]
        serialBufferPointer += 1
        if (inByte[0] == 0x0D or serialBufferPointer >= serialBufferLen):
            print("")  # flush output to terminal
            # print("")  # flush local output
            # print("==============CR============")
            # incomingCommand = serialBuffer.decode()
            incomingCommand = serialBufferToString()
            incomingCommand = incomingCommand.rstrip()

            serialBufferFlush()
            # print("incoming Command["+incomingCommand+"]")
            # procCmdRet = processCommand(incomingCommand)
            # procCmdRet = parseIncoming(incomingCommand)
            procCmdRet = parseIncomingTry(incomingCommand)
            if (procCmdRet == 1):
                print("OK\r\n")
            else:
                print("ERROR\r\n")
