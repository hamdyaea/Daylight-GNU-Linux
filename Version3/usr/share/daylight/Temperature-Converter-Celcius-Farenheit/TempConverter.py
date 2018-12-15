# Developer : Hamdy Abou El Anein

from easygui import *
import sys

logo = "/usr/share/daylight/Temperature-Converter-Celcius-Farenheit/images/term.gif"

celcius = 0
farenheit = 0
convFinal = " "

def begin():
    image = logo
    msg = "Please select if you want to convert C° Celcius or F° Farenheit"
    choices = ["Celcius", "Farenheit"]
    reply = buttonbox(msg, image=image, choices=choices)
    if reply == "Celcius":
        convertCel()
    elif reply == "Farenheit":
        convertFar()
    else:
        sys.exit(0)



def convertCel():
    global convFinal
    msg = "Enter the Celcius C° Temperature to convert in Farenheit F°"
    title = "Convert to celcius"
    fieldNames = 0
    fieldValues = 0
    fieldValues = enterbox(msg, title, fieldNames)
    celcius =  float(fieldValues)
    calcTotal = (celcius * 1.8 + 32)
    convFinal = str(calcTotal)+str(" F° Farenheit")
    final()


def convertFar():
    global convFinal
    msg = "Enter the Farenheit F° Temperature to convert in Celcius C° "
    title = "Convert to celcius"
    fieldNames = 0
    fieldValues = 0
    fieldValues = enterbox(msg, title, fieldNames)
    farenheit = float(fieldValues)
    calcTotal = ((farenheit - 32) / 1.8)
    convFinal = str(calcTotal)+str(" C° Celcius")
    final()

def final():
    global celcius, farenheit,convFinal
    msg = "This is the converted temperature :"
    title = "Temperatures converter"
    text = convFinal
    fieldValues = textbox(msg, title, text)

    celcius = float(fieldValues[0])
    farenheit = float(fieldValues[1])

begin()
