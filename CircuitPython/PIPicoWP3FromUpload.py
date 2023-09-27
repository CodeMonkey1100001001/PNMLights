# SPDX-FileCopyrightText: 2023 Michał Pokusa
#
# SPDX-License-Identifier: Unlicense
# post upload
# curl -v -F filename=rainbow.pnm -F upload=@rainbow.pnm http://192.168.99.52/api/
# curl -v -F filename=rainbow.pnm -F upload=@rainbow.pnm http://192.168.99.52/api/

from gc import mem_free,collect


import socketpool
import wifi
import time
import board
import neopixel
# Update this to match the number of NeoPixel LEDs connected to your board.
num_pixels = 16*16

#pixels = neopixel.NeoPixel(board.GP0, num_pixels)
#pixels.brightness = 0.5
pixel_pin = board.GP0
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)

pixels.fill((255,0,0))
pixels.show()
time.sleep(0.5)
pixels.fill((0,255,0))
pixels.show()
time.sleep(0.5)
pixels.fill((0,0,255))
pixels.show()
time.sleep(0.5)
pixels.fill((0,0,0))
pixels.show()
time.sleep(0.5)

pixels[0]=(255,0,0)
pixels[1]=(0,255,0)
pixels[2]=(0,0,255)
pixels[3]=(255,255,0)
pixels.show()

from adafruit_httpserver import Server, Request, JSONResponse, GET, POST, PUT, DELETE

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))


pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, debug=True)

objects = [
    {"id": 1, "name": "Object 1"},
]

def getPosInt(theData):
    try:
        retV = int(theData)
        return retV
    except:
        return -1


@server.route("/api", [GET, POST, PUT, DELETE], append_slash=True)
def api(request: Request):
    print("mem",mem_free())
    """
    Performs different operations depending on the HTTP method.
    """

    # Get objects
    if request.method == GET:
        return JSONResponse(request, objects)

    # Upload or update objects
    if request.method in [POST, PUT]:
        #uploaded_object = request.json()
        print("mem2",mem_free())
        data = request.form_data  # e.g. r=255&g=0&b=0 or r=255\r\nb=0\r\ng=0
        # print("data",data)
        #dump(data)
        print("============image[",data['upload'],"]")
        uploaded_object = "---null---"

        memstart = mem_free()
        print("mem3",mem_free())
        # gonna do it brute force memory wise first will eat a lot of ram
        if data['upload'][0:2] == b"P3":
            dataLines = data['upload'].splitlines()
            print("dl0",dataLines[0],type(dataLines[0]))
            print("P3 file")
            # decode P3 file
            size = dataLines[2].decode('utf8')
            print("size",size)
            sizeSplit = size.split(" ")
            print("sizeSplit",sizeSplit)
            xDimension=getPosInt(sizeSplit[0])
            yDimension=getPosInt(sizeSplit[1])
            #print("x,y",x,y)
            disableZigZag = False
            for y in range(0,yDimension):
                for x in range(0,xDimension):
                    if disableZigZag or (y % 2) == 0:  # normal Direction
                        # the 4 here is to ignore the first 4 lines of the file
                        rPos = 4 + (xDimension * 3 * y) + 3 * x + 0
                        gPos = 4 + (xDimension * 3 * y) + 3 * x + 1
                        bPos = 4 + (xDimension * 3 * y) + 3 * x + 2
                    else:
                        rPos = 4 + (xDimension * 3 * y) + xDimension * 3 - 3 * x -3
                        gPos = 4 + (xDimension * 3 * y) + xDimension * 3 - 3 * x -2 
                        bPos = 4 + (xDimension * 3 * y) + xDimension *3 - 3 * x  -1
                    
                    r = getPosInt(dataLines[rPos])
                    g = getPosInt(dataLines[gPos])
                    b = getPosInt(dataLines[bPos])
                    # print("y,x,pp,rgb",y,x,(y*xDimension)+x,r,g,b)
                    pixels[ (y*xDimension ) + x] = (r,g,b)
            #print("ready to show")
            pixels.show()
        if data['upload'][0:2] == b'P4':
            print("type P4")
        else:
            print("not a p3 file")
        #for line in data['upload'].splitlines():
            #print("mem loop",mem_free())
            #print(line)

        print("memstart",memstart,"memend",mem_free())
        #collect()
        #time.sleep(2)
        print("memstart",memstart,"memend",mem_free())
        #Find object with same ID
        #for i, obj in enumerate(objects):
            #if obj["id"] == uploaded_object["id"]:
                #objects[i] = uploaded_object

                #return JSONResponse(
                    #request, {"message": "Object updated", "object": uploaded_object}
                #)

        #If not found, add it
        #objects.append(uploaded_object)
        return JSONResponse(
            request, {"message": "Object added", "object": uploaded_object}
        )

    # Delete objects
    if request.method == DELETE:
        deleted_object = request.json()

        # Find object with same ID
        for i, obj in enumerate(objects):
            if obj["id"] == deleted_object["id"]:
                del objects[i]

                return JSONResponse(
                    request, {"message": "Object deleted", "object": deleted_object}
                )

        # If not found, return error
        return JSONResponse(
            request, {"message": "Object not found", "object": deleted_object}
        )

    # If we get here, something went wrong
    return JSONResponse(request, {"message": "Something went wrong"})


server.serve_forever(str(wifi.radio.ipv4_address))
