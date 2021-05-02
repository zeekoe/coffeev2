import pygame, datetime, time, os
from mpd import MPDClient
from kwidgets import KProgressBar


class MPDisplay:
	def __init__(self, scherm1, myhal1):
		self.ticker = 0
		self.scherm = scherm1
		self.myhal = myhal1
		self.fn = 'volgende'
		self.mode = 0
		self.modets = 0
		self.c = MPDClient()  # create client object
		self.c.timeout = 1  # network timeout in seconds (floats allowed), default: None
		self.c.idletimeout = None  # timeout for fetching the result of the idle command is handled seperately, default: None
		self.c.connect("192.168.1.120", 6600)  # connect to localhost:6600
		print(self.c.mpd_version)  # print the MPD version
		self.c.iterate = True
		self.pos = ""
		self.updateList()
		try:
			self.aantal = self.myhal.getAantal()
		except Exception as e:
			print("Fout in koffiezetter: " + str(e))
		self.fnlist = {1: 'volgende', 2: 'vorige', 4: 'afspelen', 3: 'schermwissel', 5: 'woonkamer'}
		self.c2 = None;
		self.kp = KProgressBar(self.scherm, 0, 0, 20, 236, 1000)
		self.kp.setColors((0, 128, 255), (0, 255, 255))

	def updateList(self):  # update list of directories / songs
		self.dirs = ['Afspelen']
		if self.pos != "":
			self.dirs.append('Omhoog')
		for el in self.c.lsinfo(self.pos):
			if 'directory' in el:
				self.dirs.append(el['directory'])
		self.listStart = 0
		self.listPos = 0

	def quit(self):
		self.c.close()  # send the close command
		self.c.disconnect()  # disconnect from the server

	def knop(self):  # handle button press
		if (self.fn == 'schermwissel'):
			if (time.time() - self.modets) > 1:
				self.mode = abs(self.mode - 1)
				self.modets = time.time()
		#		elif(self.fn == 'woonkamer'):
		#			self.copyTo('192.168.1.8')
		if (self.mode == 0):
			while (self.myhal.getStartValue() == 0):
				if (self.fn == 'volgende'):
					self.listPos += 1
				elif (self.fn == 'vorige'):
					self.listPos -= 1
				time.sleep(.25)
				if (self.myhal.getIsReal() == False):
					break
			if (self.fn == 'afspelen'):
				if self.curListItem == 'Omhoog':  # up a level
					self.pos = ''
					self.updateList()
				else:
					self.pos = self.curListItem
					self.updateList()
				if self.curListItem == 'Afspelen' or len(
						self.dirs) < 4:  # play if the 'Play' entry is selected, or if the only sub directories are '.', '..' and one 'real' dir.
					self.c.clear()
					self.c.add(self.pos)
					self.c.play()
					self.mode = 1
					self.pos = ""
					self.updateList()
		if (self.mode == 1):
			while (self.myhal.getStartValue() == 0):
				if (self.fn == 'volgende'):
					self.c.next()
				elif (self.fn == 'vorige'):
					self.c.previous()
				time.sleep(.25)
				if (self.myhal.getIsReal() == False):
					break

	def formattime(self, time):
		if time.find(':') > -1:
			tmp = time.partition(':')
			time = tmp[0]
		m = int(int(time) / 60)
		s = int(int(time) % 60)
		return str(m) + ':' + str(s).zfill(2)

	def getfn(self):
		self.aantal = self.myhal.getAantal()
		if self.aantal in self.fnlist:
			self.fn = self.fnlist[self.aantal]
		else:
			self.fn = ''

	def update(self):
		self.ticker += 1
		if self.ticker % 8 == 0:
			if os.system("ps -A | grep snapclient") != 0:  # check if snapclient is still running
				print("start snapclient")
				os.system("sudo snapclient -d -h 192.168.1.120")
				self.kp.setColors((0, 128, 255), (0, 255, 255))
		self.getfn()

		font = pygame.font.Font(None, 20)

		if self.mode == 0:
			i = -1
			j = 0
			self.curListItem = ""
			for d in self.dirs:
				i += 1
				if (i < self.listPos):
					continue
				j += 1
				if (self.curListItem == ""):
					self.curListItem = d
				if (j > 12):
					break
				text = font.render(d, 1, (0, 0, 0))
				self.scherm.blit(text, (25, j * 16))
				self.kp.setMaxval(len(self.dirs))
				self.kp.update(len(self.dirs) - self.listPos)
		else:
			info = self.c.currentsong()
			status = self.c.status()
			track = '0'
			if 'artist' in info:
				text = font.render(info['artist'], 1, (0, 0, 0))
				self.scherm.blit(text, (25, 40))
			if 'album' in info:
				text = font.render(info['album'], 1, (0, 0, 0))
				self.scherm.blit(text, (25, 56))
			if 'track' in info:
				track = info['track']
			if 'title' in info:
				text = font.render(track + ' - ' + info['title'], 1, (0, 0, 0))
				# {'songid': '17', 'playlistlength': '5', 'playlist': '14', 'repeat': '0', 'consume': '0', 'mixrampdb': '0.000000', 'random': '0', 'state': 'play', 'xfade': '0', 'volume': '91', 'single': '0', 'mixrampdelay': 'nan', 'nextsong': '1', 'time': '586:813', 'song': '0', 'elapsed': '585.596', 'bitrate': '128', 'nextsongid': '18', 'audio': '44100:24:2'}
				self.scherm.blit(text, (25, 72))
			timeok = 0
			if 'time' in info:
				text = font.render(self.formattime(info['time']), 1, (0, 0, 0))
				self.scherm.blit(text, (25, 88))
				timeok = timeok + 1
			if 'time' in status:
				text = font.render(self.formattime(status['time']), 1, (0, 0, 0))
				self.scherm.blit(text, (25, 106))
				timeok = timeok + 1
			if timeok == 2:
				print(self.timeToSeconds(self.formattime(info['time'])))
				print(self.timeToSeconds(self.formattime(status['time'])))
				self.kp.setMaxval(self.timeToSeconds(self.formattime(info['time'])))
				self.kp.update(self.timeToSeconds(self.formattime(info['time'])) - self.timeToSeconds(
					self.formattime(status['time'])))

		text = font.render(datetime.datetime.now().strftime("%H:%M"), 1, (0, 0, 0))
		self.scherm.blit(text, (444, 2))

		self.drawfn()

	def timeToSeconds(self, input):
		a = input.split(':')
		return int(a[0]) * 60 + int(a[1])

	def drawfn(self):
		self.drawfnlist(self.fnlist, self.fn)

	def drawfnlist(self, fnlist, selected):  # menu items (reorder for weird turn button numbering :-))
		font = pygame.font.Font(None, 18)
		pos = 0
		if self.myhal.getIsReal() == False:
			order = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
		else:
			order = {1: 5, 2: 3, 3: 4, 4: 1, 5: 2}
		for key in order:
			newkey = order[key]
			if newkey in fnlist:
				if fnlist[newkey] == selected:
					pygame.draw.rect(self.scherm, (0, 0, 0), (25 + pos - 2, 209, 90, 17), 1)
				text = font.render(fnlist[newkey], 1, (0, 0, 0))
				self.scherm.blit(text, (25 + pos, 210))
			pos += 90
