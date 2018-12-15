# developer : Hamdy Abou El Anein

from easygui import *
import random
import sys



dice1 = "/usr/share/daylight/dice-simulator/images/dice1.gif"
dice2 = "/usr/share/daylight/dice-simulator/images/dice2.gif"
dice3 = "/usr/share/daylight/dice-simulator/images/dice3.gif"
dice4 = "/usr/share/daylight/dice-simulator/images/dice4.gif"
dice5 = "/usr/share/daylight/dice-simulator/images/dice5.gif"
dice6 = "/usr/share/daylight/dice-simulator/images/dice6.gif"


def dice():
    inputNum = 6
    outputNum = list(range(inputNum + 1))
    outputNum.remove(0)


    numbers = random.shuffle(outputNum)


    top6 = outputNum[:1]

    if top6 == [1]:
        image=dice1
    elif top6 == [2]:
        image=dice2
    elif top6 == [3]:
        image=dice3
    elif top6 == [4]:
        image=dice4
    elif top6 == [5]:
        image=dice5
    else:
        image=dice6



    diceChoice = ["Replay","Quit"]

    replay = buttonbox(image=image,choices=diceChoice,title="Dice simulator", msg="Dice simualtor\n\nNumber on the dice : " + str(top6))
    if replay == "Replay":
        dice()
    else :
        sys.exit(0)

logoDice = "/usr/share/daylight/dice-simulator/images/dice-full.gif"
msg = "Do you want to play ?"
choices = ["Yes","No"]

begining = buttonbox(msg,image=logoDice,choices=choices)

if begining == "Yes":
    dice()
else :
    sys.exit(0)
