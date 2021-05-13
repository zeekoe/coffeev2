#!/usr/bin/python3
import sys, signal, time, platform

# load modules
from sysd import SysD
from nsdisplay import NSDisplay
from koffiezetter import Koffiezetter
# from mpdisplay import MPDisplay
from kdisplay import KDisplay

# autodetect if we are on the real platform, or in simulation mode
if platform.machine() == 'armv6l':
	from myhal import myhal
else:
	from myhald import myhal

# callback for the "Start" button. Depending on the displayed screen, the button press is redirected to the correct
# module.
def startcb(gpio, level, tick):
	print("startcb", gpio, level)
	time.sleep(.1)  # debounce
	level = myhal.getStartValue()
	if level == 0:
		uiState = myhal.getStateSwitch(kdisplay)
		print("uiState: ", uiState)
		if uiState == 0:
			koffiezetter.start(myhal.getAantal())
		elif uiState == 2:
			try:
				# mpdc.knop()
				pass
			except Exception as e:
				print("Error in mpdc-buttonpress: ", str(e))
		elif uiState == 3:
			try:
				sysd.doAction()
			except Exception as e:
				print("Error in sysd-action: ", str(e))
	else:
		print("startcb debounced")


myhal = myhal(startcb)

kdisplay = KDisplay(myhal.getIsReal())

# Ctrl+C is pressed or some other error; stop pumping and everything if something goes wrong. I implemented this
# quite soon while developing. ;-)
def sigint_handler(signum, frame):
	global myhal
	print("Interrupt! Stop the pump!")
	myhal.stopAll()
	# mpdc.quit()
	sys.exit(1)


signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigint_handler)

mpdc = None
sysd = SysD(kdisplay, myhal)

koffiezetter = Koffiezetter(kdisplay, myhal)

uiState = 0
nsd = None
rd = None

while 1:
	kdisplay.tick()
	n = myhal.getAantal()
	try:
		koffiezetter.update()
	except Exception as e:
		myhal.stopAll()
		print("Error in koffiezetter-update, stop everything: ", str(e))
	try:
		uiState = myhal.getStateSwitch(kdisplay)  # find display mode (uiState) from buttons
	except Exception as e:
		print("Waarschuwing: ", str(e))
	if uiState == 0:
		try:
			koffiezetter.updateUi()
			sysd.setSubMode(0)
		except Exception as e:
			print("Waarschuwing: ", str(e))
	elif uiState == 1:
		try:
			kdisplay.clear()
			if n == 1:
				pass
			# if nsd == None:
			# 	nsd = NSDisplay(background, myhal)
			# nsd.update()
		except Exception as e:
			print("Waarschuwing: ", str(e))
	elif uiState == 2:
		try:
			pass
		# background.fill((250, 250, 250))
		# if mpdc == None:
		# 	mpdc = MPDisplay(background, myhal)
		# mpdc.update()
		except Exception as e:
			print("Waarschuwing: ", str(e))
	else:
		kdisplay.clear()
		sysd.update()
	kdisplay.update()
