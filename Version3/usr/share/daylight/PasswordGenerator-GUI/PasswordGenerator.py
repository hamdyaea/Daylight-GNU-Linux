#Developer : Hamdy Abou El Anein

import string
import random
from easygui import *

imgPass = "/usr/share/daylight/PasswordGenerator-GUI/images/password.gif"

def generatePassword(num):

    password = ''

    for n in range(num):
        x = random.randint(0, 94)
        password += string.printable[x]

    return password


newPass = generatePassword(100)
msg = "Enter the size of the password (in number)"
title = "Password generator"
fieldNames = ["8"]
fieldValues = 0
fieldValues = enterbox(msg,title, fieldNames)

image = imgPass



message = "This is your new password : "+str(newPass[:int(fieldValues)])
msgCenter = message.center(80)
choices = ["Ok"]
reply = buttonbox(msgCenter, image=image, choices=choices)
