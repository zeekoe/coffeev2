#!/usr/bin/python2.7
import os, sys, pygame, signal, datetime, time, math, httplib2, socket, re, platform
from pygame.locals import *
from array import *

from sysd import SysD
from nsdisplay import NSDisplay
from koffiezetter import Koffiezetter
from mpdisplay import MPDisplay

if platform.machine()=='armv6l':
	from myhal import myhal
else:
	from myhald import myhal

def startcb(gpio, level, tick):
	print("startcb",gpio,level)
	time.sleep(.1)
	level = myhal.getStartValue()
	if(level == 0):
		uiState = myhal.getStateSwitch()
		print "uiState: ", uiState
		if uiState == 0:
			koffiezetter.start()
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


def sigint_handler(signum, frame):
	global myhal
	print("Interrupt! Stop the pump!")
	mpdc.quit()
	myhal.stopAll()
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
pygame.mixer.quit()

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
koffiezetter = Koffiezetter(background, myhal)

clock = pygame.time.Clock()

uiState = 0
nsd = None

while 1:
	clock.tick(4)
	try:
		koffiezetter.update()
	except Exception, e:
		myhal.stopAll()
		print "Error in koffiezetter-update, stop everything: " + str(e)
	try:
		uiState = myhal.getStateSwitch()
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
			if nsd == None:
				nsd = NSDisplay(background, myhal)
			nsd.update()
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
