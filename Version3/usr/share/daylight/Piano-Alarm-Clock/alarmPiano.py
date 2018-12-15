# Developer : Hamdy Abou El Anein

from easygui import *
import time
import webbrowser
import random

piano = "./images/piano.gif"

def setAlarm():
    msg = "What time do you want to wake up?\n\nUse this form : 08:30"
    title = "Piano alarm clock"
    fieldNames = 0
    fieldValues = enterbox(msg, title, fieldNames)
    Alarm = fieldValues
    Time = time.strftime("%H:%M")

    image = piano
    msg = "The Piano Alarm Clock is configured to start at "+str(fieldValues)+str( "\n\nYou can close this window")
    choices = ["OK"]
    reply = buttonbox(msg, image=image, choices=choices)

    with open("sound.txt") as f: #You can add some youtube video

        content = f.readlines()

    while Time != Alarm:

        Time = time.strftime("%H:%M")

        time.sleep(1)

    if Time == Alarm:

        random_video = random.choice(content) #Random choice for sound source in sound.txt

        webbrowser.open(random_video)

setAlarm()