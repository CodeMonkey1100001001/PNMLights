#!/usr/bin/python
# tested on kubuntu 21.10 desktop
# this software sends a .pnm file over serial to a device that will display it
import serial
import time
import argparse


# Do any string cleanup before sending
def fixifyData(string):
    return string


parser = argparse.ArgumentParser(description='Command line basic gcode sender for marlin polargraph')
parser.add_argument('-p', '--port', help='Input USB port', required=True)
parser.add_argument('-b', '--bps', help='USB bps', required=False, default=115200)
parser.add_argument('-f', '--file', help='Gcode file to send', required=True)
args = parser.parse_args()

# show values
print("USB Port: %s" % args.port)
print("USB Speed: %s" % args.bps)
print("File: %s" % args.file)

fileToOpen = args.file

# Open serial port
# s = serial.Serial('/dev/ttyACM0',115200)
s = serial.Serial(args.port, 115200)
print('Opening Serial Port')

num_lines = sum(1 for _ in open(args.file))

# fileToOpen = "/tmp/misc/rainbow.pnm"
# fileToOpen = "/tmp/misc/white.pnm"
# fileToOpen = "/tmp/misc/arrow.pnm"

f = open(fileToOpen, 'r')
print('Opening File')

print('Sending File')

# Stream file
lineCount = 0

startTime = time.time()

for line in f:
    lineCount += 1
    lStripped = fixifyData(line)
    lStripped = lStripped.strip()  # Strip all EOL characters for streaming
    print(lineCount, "line", lStripped)
    toSend = lStripped + '\r'
    toSend = toSend.encode('utf_8')
    s.write(toSend)
    print(s.read_until(b'\n'))
    #print(s.readall())
    s.flush()
    # time.sleep(0.025)
f.close()
s.close()
