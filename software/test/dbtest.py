#!/usr/bin/python2.7
import os, sys
import pygame
from pygame.locals import *
import signal
import time
from array import *
from pysqlite2 import dbapi2 as sqlite
import datetime

try:
	con = sqlite.connect("/home/pi/code/koffiepy/koffie.db", detect_types=sqlite.PARSE_COLNAMES)
	cur = con.cursor()
#	cur.execute("insert into koffie(aantal,datum) values(?, ?)", (2, datetime.datetime.now()))
	con.commit()
	cur.close()
	con.close()
except Exception, e:
	print "Fout bij schrijven naar database: " + str(e)
