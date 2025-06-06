import time
from kdisplay import KDisplay
maalteller = 0
pompteller = 0


class myhal:
	def __init__(self, startcb):
		self.dummyboil = 0
		self.dummypump = 0
		self.dummygrind = 0
		self.cbf = startcb
		self.aantalBuffer = 2
		self.s1Buffer = 1
		self.s2Buffer = 1
		self.dBuffer = 0

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

	def setLight(self, value):
		pass

	def uiExtra(self):
		return ""

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
		if (self.dummygrind):
			maalteller -= 10
		if (self.dummypump):
			pompteller -= 10
		return 98

	def stopAll(self):
		self.stopBoil()
		self.stopPump()
		self.stopGrind()

	def getStartValue(self):
		return 0

	def getStateSwitch(self, display: KDisplay):
		key = display.get_key()
		if key == '1':
			self.aantalBuffer = 1
		elif key == '2':
			self.aantalBuffer = 2
		elif key == '3':
			self.aantalBuffer = 3
		elif key == '4':
			self.aantalBuffer = 4
		elif key == '5':
			self.aantalBuffer = 5
		elif key == 'q':
			self.s1Buffer = abs(self.s1Buffer - 1)
		elif key == 'w':
			self.s2Buffer = abs(self.s2Buffer - 1)
		elif key == 'd':
			self.dBuffer = abs(self.dBuffer - 1)
		elif key == ' ':
			self.cbf(0, 0, 0)
		return self.s1Buffer + 2 * self.s2Buffer

	def resetDorst(self):
		pass

	def shutdown(self):
		pass
