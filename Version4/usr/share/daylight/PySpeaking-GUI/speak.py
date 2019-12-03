#!/usr/bin/env python3

# Developer : Hamdy Abou El Anein
# hamdy.aea@protonmail.com

import os
import sys
from easygui import *


class Speak:
    def __init__(self):
        self.lang
        self.fieldValues


print(
    "IMPORTANT\n\nThis software work only if google_speech is installed on the system. To install it go to this link please : https://pypi.python.org/pypi/google_speech/\n\n"
)


def language():
    msg = "What's the language do you want to make PySpeaking speak ?"
    title = "PySpeaking-GUI"
    choices = [
        "English",
        "French",
        "German",
        "Spanish",
        "Japanese",
        "Chinese",
        "Italian",
        "Arabic",
        "Russian",
    ]
    choice = choicebox(msg, title, choices)

    if choice == "English":
        Speak.lang = " en "
        textToSpeak()
    elif choice == "French":
        Speak.lang = " fr "
        textToSpeak()
    elif choice == "German":
        Speak.lang = " de "
        textToSpeak()
    elif choice == "Spanish":
        Speak.lang = " es "
        textToSpeak()
    elif choice == "Japanese":
        Speak.lang = " ja "
        textToSpeak()
    elif choice == "Chinese":
        Speak.lang = " zh-CN "
        textToSpeak()
    elif choice == "Italian":
        Speak.lang = " it "
        textToSpeak()
    elif choice == "Arabic":
        Speak.lang = " ar "
        textToSpeak()
    elif choice == "Russian":
        Speak.lang = " ru "
        textToSpeak()
    else:
        sys.exit(0)


def textToSpeak():
    msg = "Enter the text to speak"
    title = "Enter the text to speak"
    fieldNames = ["Text to speak"]
    Speak.fieldValues = []
    Speak.fieldValues = multenterbox(msg, title, fieldNames)
    Speak.fieldValues[0]
    speak()


def speak():
    textValue = (
        "google_speech -l"
        + str(Speak.lang)
        + str(' "')
        + str(Speak.fieldValues[0].replace("'", "'"))
        + str('"')
    )
    os.system(textValue)


language()
