#!/bin/bash

curl  https://caeszar:0723050504@mail.google.com/mail/feed/atom -s | grep fullcount | tail -c +12 | head -c -13


