#!/usr/bin/python2.7
import sys, pygame, signal, time, platform
from pygame.locals import *
from array import *

# load modules
from sysd import SysD
from nsdisplay import NSDisplay
from raindisplay import RainDisplay
from koffiezetter import Koffiezetter
from mpdisplay import MPDisplay
from telegram import TGCoffeeBot

# autodetect if we are on the real platform, or in simulation mode
if platform.machine()=='armv6l':
	from myhal import myhal
else:
	from myhald import myhal

# callback for the "Start" button. Depending on the displayed screen, the button press is redirected to the correct module.
def startcb(gpio, level, tick):
	print("startcb",gpio,level)
	time.sleep(.1) # debounce
	level = myhal.getStartValue()
	if(level == 0):
		uiState = myhal.getStateSwitch()
		print "uiState: ", uiState
		if uiState == 0:
			koffiezetter.start(myhal.getAantal())
		elif uiState == 2:
			try:
				mpdc.knop()
			except Exception, e:
				print "Error in mpdc-buttonpress: " + str(e)
		elif uiState == 3:
			try:
				sysd.doAction()
			except Exception, e:
				print "Error in sysd-action: " + str(e)
	else:
		print("startcb debounced")

myhal = myhal(startcb)


# Ctrl+C is pressed or some other error; stop pumping and everything if something goes wrong. I implemented this quite soon while developing. ;-)
def sigint_handler(signum, frame):
	global myhal
	print("Interrupt! Stop the pump!")
	bot.sender("Bye!",0)
	myhal.stopAll()
	bot.stop_polling()
	mpdc.quit()
	sys.exit(1)

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigint_handler)

pygame.init()
if myhal.getIsReal():
	screen = pygame.display.set_mode((480, 236), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
else:
	screen = pygame.display.set_mode((480, 236));
pygame.display.set_caption('Koffie!')
pygame.mouse.set_visible(0)
pygame.mixer.quit() # this saves >25% CPU...

background = pygame.Surface(screen.get_size())
background = background.convert()
# background.fill((250, 250, 250))
plaatje = pygame.image.load('/var/www/scherm.png')
plaatje.convert()
background.blit(plaatje, (0,0))

screen.blit(background, (0, 0))
pygame.display.flip()
mpdc = None
sysd = SysD(background, myhal)

def botsender(msg,sleep):
	bot.sender(msg,sleep)

koffiezetter = Koffiezetter(background, myhal, botsender)

bot = TGCoffeeBot(koffiezetter.handle_bot_message)


clock = pygame.time.Clock()

uiState = 0
nsd = None
rd = None

while 1:
	clock.tick(4) # screen refresh rate / clock tick are fixed to 4 FPS
	n = myhal.getAantal()
	try:
		koffiezetter.update()
	except Exception, e:
		myhal.stopAll()
		print "Error in koffiezetter-update, stop everything: " + str(e)
	try:
		uiState = myhal.getStateSwitch() # find display mode (uiState) from buttons
	except Exception, e:
		print "Waarschuwing: " + str(e)
	if uiState == 0:
		try:
			background.blit(plaatje, (0,0))
			koffiezetter.updateUi()
			sysd.setSubMode(0)
		except Exception, e:
			print "Waarschuwing: " + str(e)
	elif uiState == 1:
		try:
			background.fill((250, 250, 250))
			if n == 1:
				if nsd == None:
					nsd = NSDisplay(background, myhal)
				nsd.update()
			else:
				if rd == None:
					rd = RainDisplay(background, myhal)
				rd.update()
		except Exception, e:
			print "Waarschuwing: " + str(e)
	elif uiState == 2:
		try:
			background.fill((250, 250, 250))
			if mpdc == None:
				mpdc = MPDisplay(background, myhal)
			mpdc.update()
		except Exception, e:
			print "Waarschuwing: " + str(e)
	else:
		background.fill((250, 250, 250))
		sysd.update()
	screen.blit(background, (0, 0))
	pygame.display.flip()
