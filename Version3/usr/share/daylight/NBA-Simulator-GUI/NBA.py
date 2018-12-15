# Developer : Hamdy Abou El Anein

import random
import sys
from easygui import *

nbaMap = "/usr/share/daylight/NBA-Simulator-GUI/images/nba-map.gif"
nbaLogo = "/usr/share/daylight/NBA-Simulator-GUI/images/nbaLogo.gif"
nbaFinal = "/usr/share/daylight/NBA-Simulator-GUI/images/nbaFinal.gif"
NBAwinner = "/usr/share/daylight/NBA-Simulator-GUI/images/winneNBA.gif"

eastConf = ["Boston Celtics","Toronto Raptors","Cleveland Cavaliers","Indiana Pacers","Detroit Pistons","Milwaukee Bucks","Washington Wizards","New York Knicks","Miami Heat", "Philadelphia 76ers","Brooklyn Nets","Charlotte Hornets","Orlando Magic", "Chicago Bulls", "Atlanta Hawks"]

westConf = ["Houston Rockets","Golden State Warriors","San Antonio Spurs","Minnesota Timberwolves","Oklahoma Thunder","Denver Nuggets","Portland Trail Blazers","New-Orleans Pelicans","Utah Jazz","Los Angeles Clippers","Los Angeles Lakers","Sacramento Kings","Phoenix Suns","Memphis Grizzlies","Dallas Mavericks"]

def winnerResult():
    global  winFinalRes

    msg = "The winner is : "+str(winFinalRes[0])
    choices = ["Ok"]
    reply = buttonbox(msg,image=NBAwinner, choices=choices)
    if reply == "OK":
        sys.exit(0)
    else:
        sys.exit(0)

def NBAfinal():
    global EastResConf,WestResConf, winFinalRes

    winFinalRes=[EastResConf[0],WestResConf[0]]
    random.shuffle(winFinalRes)

    msg = "NBA final :\n\n\n"+str(EastResConf[0])+str(" VS ")+str(WestResConf[0])
    choices = ["Winner result"]
    reply = buttonbox(msg,image=nbaFinal,choices=choices)
    if reply == "Winner result":
        winnerResult()
    elif reply == "./images/nbaFinal.gif":
        winnerResult()
    else:
        sys.exit(0)

def confFinals():
    global AeastConfFinals,BeastConfFinals,AwestConfFinals,BwestConfFinals,EastResConf,WestResConf

    EastResConf=[AeastConfFinals[0],BeastConfFinals[0]]
    WestResConf=[AwestConfFinals[0],BwestConfFinals[0]]

    random.shuffle(EastResConf)
    random.shuffle(WestResConf)

    msg = "Conferences finals :\n\n"+str("Eastern conference\n\n")+str(AeastConfFinals[0])+str(" VS ")+str(BeastConfFinals[0])+str("\n\nWestern conference\n\n")+str(AwestConfFinals[0])+str(" VS ")+str(BwestConfFinals[0])
    choices = ["NBA Final"]
    reply = buttonbox(msg,image=nbaMap, choices=choices)
    if reply == "NBA Final":
        NBAfinal()
    elif reply == "./images/nba-map.gif":
        NBAfinal()
    else:
        sys.exit(0)



def confHalfFinal():
    global AeastFirstTour,BeastFirstTour,CeastFirstTour,DeastFirstTour,AwestFirstTour,BwestFirstTour,CwestFirstTour,DwestFirstTour, AeastConfFinals ,BeastConfFinals ,AwestConfFinals,BwestConfFinals

    AeastConfFinals = [AeastFirstTour[0] ,BeastFirstTour[0]]
    BeastConfFinals = [CeastFirstTour[0],DeastFirstTour[0]]
    AwestConfFinals = [AwestFirstTour[0],BwestFirstTour[0]]
    BwestConfFinals = [CwestFirstTour[0],DwestFirstTour[0]]

    random.shuffle(AeastConfFinals)
    random.shuffle(BeastConfFinals)

    random.shuffle(AwestConfFinals)
    random.shuffle(BwestConfFinals)

    msg = "Conferences half-final :\n\n"+str("Eastern conference\n\n")+str(AeastFirstTour[0])+str(" VS ")+str(BeastFirstTour[0])+str("\n")+str(CeastFirstTour[0])+str(" VS ")+str(DeastFirstTour[0])+str("\n\nWestern conference\n\n")+str(AwestFirstTour[0])+str(" VS ")+str(BwestFirstTour[0])+str("\n")+str(CwestFirstTour[0])+str(" VS ")+str(DwestFirstTour[0])
    choices = ["Conferences finals"]
    reply = buttonbox(msg,image=nbaMap, choices=choices)
    if reply == "Conferences finals":
        confFinals()
    elif reply == "./images/nba-map.gif":
        confFinals()
    else:
        sys.exit(0)

def firstTour():
    global bestBeginEast, bestBeginWest,AeastFirstTour,BeastFirstTour,CeastFirstTour,DeastFirstTour,AwestFirstTour,BwestFirstTour,CwestFirstTour,DwestFirstTour

    AeastFirstTour = [bestBeginEast[0],bestBeginEast[7]]
    BeastFirstTour = [bestBeginEast[3],bestBeginEast[4]]
    CeastFirstTour = [bestBeginEast[2],bestBeginEast[5]]
    DeastFirstTour = [bestBeginEast[1],bestBeginEast[6]]

    AwestFirstTour = [bestBeginWest[0],bestBeginWest[7]]
    BwestFirstTour = [bestBeginWest[3],bestBeginWest[4]]
    CwestFirstTour = [bestBeginWest[2],bestBeginWest[5]]
    DwestFirstTour = [bestBeginWest[1],bestBeginWest[6]]

    random.shuffle(AeastFirstTour)
    random.shuffle(BeastFirstTour)
    random.shuffle(CeastFirstTour)
    random.shuffle(DeastFirstTour)

    random.shuffle(AwestFirstTour)
    random.shuffle(BwestFirstTour)
    random.shuffle(CwestFirstTour)
    random.shuffle(DwestFirstTour)

    msg = "First-tour :\n\n"+str("Eastern conference\n\n")+str(bestBeginEast[0])+str(" VS ")+str(bestBeginEast[7])+str("\n")+str(bestBeginEast[3])+str(" VS ")+str(bestBeginEast[4])+str("\n")+str(bestBeginEast[2])+str(" VS ")+str(bestBeginEast[5])+str("\n")+str(bestBeginEast[1])+str(" VS ")+str(bestBeginEast[6])+str("\n\nWestern conference\n\n")+str(bestBeginWest[0])+str(" VS ")+str(bestBeginWest[7])+str("\n")+str(bestBeginWest[3])+str(" VS ")+str(bestBeginWest[4])+str("\n")+str(bestBeginWest[2])+str(" VS ")+str(bestBeginWest[5])+str("\n")+str(bestBeginWest[1])+str(" VS ")+str(bestBeginWest[6])
    choices = ["Conferences half-final"]
    reply = buttonbox(msg,image=nbaMap, choices=choices)
    if reply == "Conferences half-final":
        confHalfFinal()
    elif reply == "./images/nba-map.gif":
        confHalfFinal()
    else:
        sys.exit(0)

def play():
    global bestBeginEast, bestBeginWest
    random.shuffle(eastConf)
    random.shuffle(westConf)

    bestBeginEast = [eastConf[0],eastConf[1],eastConf[2],eastConf[3],eastConf[4],eastConf[5],eastConf[6],eastConf[7]]
    bestBeginWest = [westConf[0],westConf[1],westConf[2],westConf[3],westConf[4],westConf[5],westConf[6],westConf[7]]

    msg = "Best 8 Teams Eastern conference :\n\n"+str(bestBeginEast[0])+str(" , ")+str(bestBeginEast[1])+str(" , ")+str(bestBeginEast[2])+str(" , ")+str(bestBeginEast[3])+str(" , ")+str(bestBeginEast[4])+str(" , ")+str(bestBeginEast[5])+str(" , ")+str(bestBeginEast[6])+str(" , ")+str(bestBeginEast[7])+str("\n\nBest 8 Teams Western conference :\n\n")+str(bestBeginWest[0])+str(" , ")+str(bestBeginWest[1])+str(" , ")+str(bestBeginWest[2])+str(" , ")+str(bestBeginWest[3])+str(" , ")+str(bestBeginWest[4])+str(" , ")+str(bestBeginWest[5])+str(" , ")+str(bestBeginWest[6])+str(" , ")+str(bestBeginWest[7])
    choices = ["First tour"]
    reply = buttonbox(msg,image=nbaMap, choices=choices)
    if reply == "First tour":
        firstTour()
    elif reply == "./images/nba-map.gif":
        firstTour()
    else:
        sys.exit(0)

def begin():
    msg = "Welcome to the NBA championship\n\nEastern Conference\n\n"+str(eastConf[0])+str(" , ")+str(eastConf[1])+str(" , ")+str(eastConf[2])+str(" , ")+str(eastConf[3])+str(" , ")+str(eastConf[4])+str(" , ")+str(eastConf[5])+str(" , ")+str(eastConf[6])+str(" , ")+str(eastConf[7])+str(" , ")+str(eastConf[8])+str(" , ")+str(eastConf[9])+str(" , ")+str(eastConf[10])+str(" , ")+str(eastConf[11])+str(" , ")+str(eastConf[12])+str(" , ")+str(eastConf[13])+str(" , ")+str(eastConf[14])+str("\n\nWestern conference\n\n")+str(westConf[0])+str(" , ")+str(westConf[1])+str(" , ")+str(westConf[2])+str(" , ")+str(westConf[3])+str(" , ")+str(westConf[4])+str(" , ")+str(westConf[5])+str(" , ")+str(westConf[6])+str(" , ")+str(westConf[7])+str(" , ")+str(westConf[8])+str(" , ")+str(westConf[9])+str(" , ")+str(westConf[10])+str(" , ")+str(westConf[11])+str(" , ")+str(westConf[12])+str(" , ")+str(westConf[13])+str(" , ")+str(westConf[14])+str("\n\n\n\n")
    choices = ["Play"]
    reply = buttonbox(msg,image=nbaLogo, choices=choices)
    if reply == "Play":
        play()
    elif reply == "./images/nbaLogo.gif":
        play()
    else:
        sys.exit(0)


begin()
