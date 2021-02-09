#!/usr/bin/python
import sys
import os
import usb.core
import usb.util

#Find the device idVendor 0x294e / idProduct 0x1001
dev = usb.core.find(idVendor=0x0930, idProduct=0x0807)

#Select interface 0 and endpoint 0
interface = 1
endpoint = dev[0][(1,0)][0]

#Detach kernel driver
if dev.is_kernel_driver_active(interface) is True:
    dev.detach_kernel_driver(interface)
    usb.util.claim_interface(dev, interface)

collected = 0 #variable to skip the first two data
testsup = float(100)
testinf = float(127)
deplacement = testsup/testinf
sensibilite = 2.5
x = 0
y = 0
click = ""
mouse_btn_l = 0
mouse_btn_r = 0

#Infinite while
while 1:
    try:
        data = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
        collected += 1
        # print (data)
        #The 2 first data are not move data
        if collected > 2:
            #data[2] Right (2) & Left (255) = x
            #data[1] Down (1) & Up (255) = y

            # x
            if (1 <= data[2] <= 127): #Right
                 x = data[2]*deplacement*sensibilite
            elif (128 <= data[2] <= 255): #Left
                 x = -((-data[2]+256)*deplacement*sensibilite)
            else : #No move on x axis
                 x = 0

            # y
            if (1 <= data[3] <= 127): #Down
                y = data[3]*deplacement*sensibilite
            elif (128 <= data[3] <= 255): #Up
                y = -((-data[3]+256)*deplacement*sensibilite)
            else : #No move on y axis
                y = 0

            #Left click
            if data[1] == 1 and mouse_btn_l == 0:
                click = "mousedown 1"
                mouse_btn_l = 1
            #Right click
            elif data[1] == 2 and mouse_btn_r == 0:
                click = "mousedown 3"
                mouse_btn_r = 1
            #No click
            elif data[1] == 0:
                if mouse_btn_l == 1:
                    click = "mouseup 1"
                if mouse_btn_r == 1:
                    click = "mouseup 3"
                mouse_btn_l = 0
                mouse_btn_r = 0
            else:
                click = " " 


        os.system("xdotool mousemove_relative -- %d %d %s" % (x, y, click))

    #Error
    except usb.core.USBError as e:
        data = None
        if e.args == ('Operation timed out',):
            continue
usb.util.release_interface(dev, interface)