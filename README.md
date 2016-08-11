# Coffee machine v2
Coffee machine v2 source code. Check https://hackaday.io/project/12688-coffee-machine-v2/ for info.

# Dummy environment controls
The dummy environment (automatically chosen if architecture != armv6l) allows for simulating the coffee machine on a desktop computer. The following buttons can be used to control it:
* w, q: state switch buttons
* 1,2,3,4,5: number buttons
* space bar: start button
* Ctrl + C in the terminal (sometimes needed twice :-)): quit

# Installation
Check the defaults directory.

# Work in progress
* Most texts and variables were originally written in Dutch. Some are already translated to English.
* In an initial version, the MPD client connected to an MPD server on the Pi itself, while the files were accessed over CIFS/SMB. Currently, it connects to an MPD server on a different computer, and uses snapserver/snapclient to play music in sync on both computers. Code for both still is in the repository.

# Firmware
Read https://hackaday.io/project/12688-coffee-machine-v2/log/41952-ronaldboard-isp-programming-i2c-communication for the background and the neccesary files
