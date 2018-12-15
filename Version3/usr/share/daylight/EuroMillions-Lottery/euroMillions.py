# developer : Hamdy Abou El Anein

from easygui import *
import random
import sys



ticket = "/usr/share/daylight/EuroMillions-Lottery/images/ticketfull1.gif"


def lottery():
    inputNum = 50
    outputNum = list(range(inputNum + 1))
    outputNum.remove(0)
    inputSta = 12
    outputSta = list(range(inputSta + 1))
    outputSta.remove(0)

    numbers = random.shuffle(outputNum)

    stars = random.shuffle(outputSta)

    top5 = outputNum[:5]
    top2 = outputSta[:2]

    top5.sort()
    top2.sort()

    lotChoice = ["Replay"]

    replay = buttonbox(image=ticket,choices=lotChoice,title="List of numbers to play", msg="Numbers : " + str(top5) + str(" \nStars : " + str(top2)))
    if replay == "Replay":
        lottery()
    else :
        sys.exit(0)

logoLoto = "/usr/share/daylight/EuroMillions-Lottery/images/loto.gif"
msg = "Do you want to play ?"
choices = ["Yes","No"]

begining = buttonbox(msg,image=logoLoto,choices=choices)

if begining == "Yes":
    lottery()
else :
    sys.exit(0)




