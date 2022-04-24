#!/bin/bash

Xvfb $DISPLAY -ac -listen tcp -screen 0 1960x1024x24 &>/dev/null &
sleep 3
x11vnc -display $DISPLAY -forever &>/dev/null &

python3 /app/vaxiin_server.py
