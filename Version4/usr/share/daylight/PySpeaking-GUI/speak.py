# Developer : Hamdy Abou El Anein

import os
import sys
from easygui import *

print("IMPORTANT\n\nThis software work only if google_speech is installed on the system. To install it go to this link please : https://pypi.python.org/pypi/google_speech/\n\n")


def language():

    global lang

    msg = "What's the language do you want to make PySpeaking speak ?"
    title = "PySpeaking-GUI"
    choices = ["English", "French", "German", "Spanish","Japanese","Chinese","Italian","Arabic", "Russian"]
    choice = choicebox(msg, title, choices)

    if choice == "English":
        lang = ' en '
        textToSpeak()
    elif choice == "French":
        lang = ' fr '
        textToSpeak()
    elif choice == "German":
        lang = ' de '
        textToSpeak()
    elif choice == "Spanish":
        lang = ' es '
        textToSpeak()
    elif choice == "Japanese":
        lang = ' ja '
        textToSpeak()
    elif choice == "Chinese":
        lang = ' zh-CN '
        textToSpeak()
    elif choice == "Italian":
        lang = ' it '
        textToSpeak()
    elif choice == "Arabic":
        lang = ' ar '
        textToSpeak()
    elif choice == "Russian":
        lang = ' ru '
        textToSpeak()
    else:
        sys.exit(0)

def textToSpeak():
    global fieldValues

    msg = "Enter the text to speak"
    title = "Enter the text to speak"
    fieldNames = ["Text to speak"]
    fieldValues = []
    fieldValues = multenterbox(msg, title, fieldNames)
    fieldValues[0]
    speak()

def speak():
    global lang, fieldValues

    textValue = "google_speech -l" +str(lang) +str(" \"")+str(fieldValues[0].replace("'","\'"))+str("\"")
    os.system(textValue)

language()