# Developer : Hamdy Abou El Anein

from easygui import *
import sys
from random import randint

fieldValues = []
tentative = 0
def begin():
    message = "Try to guess the number. \nEnter a number between 1 and 20"
    title = "Guess The Number"
    fieldNames = ["1"]

    fieldValues = enterbox(message,title, fieldNames)
    global tentative
    tentative = tentative + 1

    if int(fieldValues) > takeOne :
        big()
    elif int(fieldValues) < takeOne :
        small()
    else :
        win()




def small():

    message = "Try again, your number is too small"
    msgCenter = message.center(80)
    choices = ["Retry", "Quit"]
    reply = buttonbox(msg=msgCenter, choices=choices)
    if reply == "Retry":
        begin()
    else :
        sys.exit(0)

def big():

    message = "Try again, your number is too big"
    msgCenter = message.center(80)
    choices = ["Retry", "Quit"]
    reply = buttonbox(msg=msgCenter, choices=choices)
    if reply == "Retry":
        begin()
    else :
        sys.exit(0)

def win():
    image = "/usr/share/daylight/Guess-the-number/images/win.gif"
    message = "Congratulation, you have found the right number ! \n\n The right number was " +str(takeOne)+str("\n\n You win after ") +str(tentative) +str(" attempt")
    msgCenter = message.center(80)
    choices = ["Quit"]
    reply = buttonbox(msg=msgCenter,image=image, choices=choices)
    if reply == "Quit":
        sys.exit(0)




takeOne =(randint(1, 20))

begin()
