# Developer : Hamdy Abou El Anein

from easygui import *
import random
import sys


child = "/usr/share/daylight/Memory-Child-Game/images/child.gif"
cop = "/usr/share/daylight/Memory-Child-Game/images/cop.gif"
girl = "/usr/share/daylight/Memory-Child-Game/images/girl.gif"
child1 = "/usr/share/daylight/Memory-Child-Game/images/child1.gif"
cop1 = "/usr/share/daylight/Memory-Child-Game/images/cop1.gif"
girl1 = "/usr/share/daylight/Memory-Child-Game/images/girl1.gif"

back1 = "/usr/share/daylight/Memory-Child-Game/images/back1.gif"
back2 = "/usr/share/daylight/Memory-Child-Game/images/back2.gif"
back3 = "/usr/share/daylight/Memory-Child-Game/images/back3.gif"
back4 = "/usr/share/daylight/Memory-Child-Game/images/back4.gif"
back5 = "/usr/share/daylight/Memory-Child-Game/images/back5.gif"
back6 = "/usr/share/daylight/Memory-Child-Game/images/back6.gif"


def game():
    global slot1, slot2, slot3, slot4, slot5, slot6, front1, front2, front3, front4, front5, front6
    inputNum = 6
    outputNum = list(range(inputNum + 1))
    outputNum.remove(0)
    numbers = random.shuffle(outputNum)

    slot1 = outputNum[0]
    if slot1 == 1:
         slot1 = back1
         front1 = child
    elif slot1 == 2:
         slot1 = back2
         front1 = cop
    elif slot1 == 3:
         slot1 = back3
         front1 = girl
    elif slot1 == 4:
         slot1 = back4
         front1 = child1
    elif slot1 == 5:
         slot1 = back5
         front1 = cop1
    else:
         slot1 = back6
         front1 = girl1

    slot2 = outputNum[1]
    if slot2 == 1:
         slot2 = back1
         front2 = child
    elif slot2 == 2:
         slot2 = back2
         front2 = cop
    elif slot2 == 3:
         slot2 = back3
         front2 = girl
    elif slot2 == 4:
         slot2 = back4
         front2 = child1
    elif slot2 == 5:
         slot2 = back5
         front2 = cop1
    else:
         slot2 = back6
         front2 = girl1



    slot3 = outputNum[2]
    if slot3 == 1:
         slot3 = back1
         front3 = child
    elif slot3 == 2:
         slot3 = back2
         front3 = cop
    elif slot3 == 3:
         slot3 = back3
         front3 = girl
    elif slot3 == 4:
         slot3 = back4
         front3 = child1
    elif slot3 == 5:
         slot3 = back5
         front3 = cop1
    else:
         slot3 = back6
         front3 = girl1


    slot4 = outputNum[3]
    if slot4 == 1:
         slot4 = back1
         front4 = child
    elif slot4 == 2:
         slot4 = back2
         front4 = cop
    elif slot4 == 3:
         slot1 = back3
         front4 = girl
    elif slot4 == 4:
         slot4 = back4
         front4 = child1
    elif slot4 == 5:
         slot4 = back5
         front4 = cop1
    else:
         slot4 = back6
         front4 = girl1

    slot5 = outputNum[4]
    if slot5 == 1:
         slot5 = back1
         front5 = child
    elif slot5 == 2:
         slot5 = back2
         front5 = cop
    elif slot5 == 3:
         slot5 = back3
         front5 = girl
    elif slot5 == 4:
         slot5 = back4
         front5 = child1
    elif slot5 == 5:
         slot5 = back5
         front5 = cop1
    else:
         slot5 = back6
         front5 = girl1

    slot6 = outputNum[5]
    if slot6 == 1:
         slot6 = back1
         front6 = child
    elif slot6 == 2:
         slot6 = back2
         front6 = cop
    elif slot6 == 3:
         slot6 = back3
         front6 = girl
    elif slot6 == 4:
         slot6 = back4
         front6 = child1
    elif slot6 == 5:
         slot6 = back5
         front6 = cop1
    else:
         slot6 = back6
         front6 = girl1

def begin():
    global slot1, slot2, slot3, slot4, slot5, slot6, front1, front2, front3, front4, front5, front6
    image = slot1, slot2, slot3, slot4, slot5, slot6
    msg = "                               Memory children Game\n\nEvery player select two cards\n\nIf the two cards are the same the player win 1 point"
    choices = []
    reply = buttonbox(msg, image=image, choices=choices)

    if reply == "/usr/share/daylight/Memory-Child-Game/images/back1.gif":
        image = front1
        msg = []
        choices = []
        reply = buttonbox(msg, image=image, choices=choices)
        begin()

    elif reply == "/usr/share/daylight/Memory-Child-Game/images/back2.gif":
        image = front2
        msg = []
        choices = []
        reply = buttonbox(msg, image=image, choices=choices)
        begin()

    elif reply == "/usr/share/daylight/Memory-Child-Game/images/back3.gif":
        image = front3
        msg = []
        choices = []
        reply = buttonbox(msg, image=image, choices=choices)
        begin()

    elif reply == "/usr/share/daylight/Memory-Child-Game/images/back4.gif":
        image = front4
        msg = []
        choices = []
        reply = buttonbox(msg, image=image, choices=choices)
        begin()

    elif reply == "/usr/share/daylight/Memory-Child-Game/images/back5.gif":
        image = front5
        msg = []
        choices = []
        reply = buttonbox(msg, image=image, choices=choices)
        begin()

    elif reply == "/usr/share/daylight/Memory-Child-Game/images/back6.gif":
        image = front6
        msg = []
        choices = []
        reply = buttonbox(msg, image=image, choices=choices)
        begin()

    else:
        sys.exit(0)


game() 
begin()
