# Developer : Hamdy Abou El Anein
import datetime
from datetime import date
from easygui import *

calendar = "./images/calendar.gif"
yearBirth = 0
monthBirth = 0
dayBirth = 0
msg = "Enter all your informations"
title = "All your informations"
fieldNames = ["Your Firstname","Year of birth", "Month of birth", "Day of Birth"]
birthValues = []
birthValues = multenterbox(msg, title, fieldNames)
yourName = birthValues[0]
yearBirth = birthValues[1]
monthBirth = birthValues[2]
dayBirth = birthValues[3]


#todayYear = 0
#todayMonth = 0
#todayDay = 0
#msg = "Enter the date of today"
#title = "Date of today"
#fieldNames = ["Year", "Month", "Day"]
#todayValues = []
#todayValues = multenterbox(msg, title, fieldNames) # Enter manualy the values
#todayYear = todayValues[0]
#todayMonth = todayValues[1]
#todayDay = todayValues[2]


#d0 = date(int(todayYear), int(todayMonth), int(todayDay)) #today Year,Month,Day, if manual values
d1 = date(int(yearBirth), int(monthBirth), int(dayBirth)) #date in past Year,Month,Day

now = datetime.datetime.now()
d0 = date(now.year, now.month, now.day)
delta = d0 - d1

image = calendar
message = "Congratulation "+str(yourName)+str(", you lived ") +str(delta.days) +str(" days until today !")
msgCenter = message.center(80)
choices = ["Ok"]
reply = buttonbox(msg=msgCenter, image=image, choices=choices)

