#!/usr/bin/python3
# Developer : Hamdy Abou El Anein

from easygui import *

image = "/usr/share/daylight/daylightstart/DayLightLogoSunSet.gif"
msg = "              Welcome to Daylight Linux\n\n\n              The lighter you become, the more you are able to run."
choices = ["Daylight Linux"]
buttonbox(msg, image=image, choices=choices)
