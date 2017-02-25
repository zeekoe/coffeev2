import time, pygame

maalteller = 0
gpiostate = {0:0}
pompteller = 0

class myhal:
	def __init__(self, startcb):
		self.dummyboil = 0
		self.dummypump = 0
		self.dummygrind = 0
		gpiostate = {17:0, 27:0, 22:0, 4:0, 0:0}
		self.cbf = startcb
		self.aantalBuffer = 2
		self.s1Buffer = 1
		self.s2Buffer = 0
		self.dBuffer = 1
	
	def getIsReal(self):
		return 0
		
	def getMaalteller(self):
		global maalteller
		return maalteller
	def setMaalteller(self, mt):
		global maalteller
		maalteller = mt
	def setPompteller(self, pt):
		global pompteller
		pompteller = pt
	def getPompteller(self):
		global pompteller
		return pompteller

	def getAantal(self):
		return self.aantalBuffer
	def setLight(self,value):
		print "light: " + str(value)
	def doCount(self):
		print("counting")
		time.sleep(.5)
	def doBoil(self):
		self.dummyboil = 1
		print("startboil")
	def stopBoil(self):
		self.dummyboil = 0
		print("stopboil")
	def doPump(self):
		self.dummypump = 1
		print("dopump")
	def stopPump(self):
		self.dummypump = 0
		print("stoppump")
	def doGrind(self):
		self.dummygrind = 1
		print("dogrind")
	def stopGrind(self):
		self.dummygrind = 0
		print("stopgrind")
	def getDorst(self):
		return self.dBuffer
	def getTemperature(self):
		global maalteller
		global pompteller
		if(self.dummygrind):
			maalteller -= 10
		if(self.dummypump):
			pompteller -= 10
		return 98
	def stopAll(self):
		self.stopBoil()
		self.stopPump()
		self.stopGrind()
	def getStartValue(self):
		return 0
	def getStateSwitch(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				print "Key: ",event.key
				if event.key == pygame.K_1:
					self.aantalBuffer = 1
				elif event.key == pygame.K_2:
					self.aantalBuffer = 2
				elif event.key == pygame.K_3:
					self.aantalBuffer = 3
				elif event.key == pygame.K_4:
					self.aantalBuffer = 4
				elif event.key == pygame.K_5:
					self.aantalBuffer = 5
				elif event.key == pygame.K_q:
					self.s1Buffer = abs(self.s1Buffer - 1)
				elif event.key == pygame.K_w:
					self.s2Buffer = abs(self.s2Buffer - 1)
				elif event.key == pygame.K_d:
					self.dBuffer = abs(self.dBuffer - 1)
				elif event.key == pygame.K_SPACE:
					self.cbf(0,0,0)
		return self.s1Buffer + 2 * self.s2Buffer
		
