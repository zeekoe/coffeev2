import smbus
import pigpio
import time
import os

maalteller = 0
gpiostate = {0: 0}
globalpi = pigpio.pi()
pompteller = 0
maaltijd = []
maaltik = 0
pomptijd = []
pomptik = 0


def gpiocb(gpio, level, tick):
	global gpiostate
	print("gpiocb", gpio, level)
	gpiostate[gpio] = level


def gpiomaalcb(gpio, level, tick):  # call back for grinder pulse
	global maalteller, maaltijd, maaltik
	if level == 0 and maalteller > 0:
		maalteller -= 1
		if maaltik != 0:
			maaltijd.append((tick - maaltik) / 1000)
			if len(maaltijd) > 4:
				maaltijd.pop(0)
			print(maaltijd)
		maaltik = tick


def gpiopompcb(gpio, level, tick):  # call back for flow meter (water pump) pulse
	global pompteller, pomptik, pomptijd
	if level == 0 and pompteller > 0:
		pompteller -= 1
		if pomptik != 0:
			pomptijd.append((tick - pomptik) / 1000)
			if len(pomptijd) > 2:
				pomptijd.pop(0)
			print(pomptijd)
		pomptik = tick


class myhal:
	def __init__(self, startcb):
		global gpiostate, globalpi
		self.showtemp = 0
		self.pi = globalpi
		self.stopAll()
		self.bus = smbus.SMBus(1)
		self.address = 0x20
		self.pi.set_pull_up_down(17, pigpio.PUD_UP)
		self.pi.set_pull_up_down(27, pigpio.PUD_UP)
		self.pi.set_pull_up_down(22, pigpio.PUD_UP)
		self.pi.set_pull_up_down(24, pigpio.PUD_UP)
		self.pi.set_pull_up_down(23, pigpio.PUD_UP)  # reserved
		self.pi.set_pull_up_down(4, pigpio.PUD_UP)
		self.pi.set_pull_up_down(31, pigpio.PUD_UP)

		gpiostate = {17: self.pi.read(17), 27: self.pi.read(27), 22: self.pi.read(22), 4: self.pi.read(4), 0: 0}

		# sleep(.5) # wait for PUD's to settle?

		self.pi.callback(22, pigpio.FALLING_EDGE, startcb)  # start button
		self.pi.callback(4, pigpio.EITHER_EDGE, gpiocb)  # thirsty
		self.pi.callback(24, pigpio.EITHER_EDGE, gpiomaalcb)  # grinder
		self.pi.callback(31, pigpio.FALLING_EDGE, gpiopompcb)  # flow meter after pump

	def getIsReal(self):
		return 1

	def getGpioValue(self, gpio):
		return self.pi.read(gpio)

	def getStartValue(self):
		return self.pi.read(22)

	def getMaalteller(self):
		global maalteller
		return maalteller

	def setMaalteller(self, mt):
		global maalteller
		maalteller = mt

	def getMaaltijd(self):
		global maaltijd
		if len(maaltijd) == 0:
			return 0
		else:
			return sum(maaltijd) / len(maaltijd)

	def getPompteller(self):
		# 1000 count units = 380 ml
		global pompteller
		return pompteller * 380 / 1000

	def setPompteller(self, pt):
		# 1000 count units = 380 ml
		global pompteller
		pompteller = pt * 1000 / 380

	def getPomptijd(self):
		global pomptijd
		if len(pomptijd) == 0:
			return 0
		else:
			return sum(pomptijd) / len(pomptijd)

	def getAantal(self):
		tmp = self.bus.read_byte_data(self.address, 0)
		if tmp == 1:
			aantal = 2
		elif tmp == 2:
			aantal = 3
		elif tmp == 4:
			aantal = 5
		elif tmp == 8:
			aantal = 4
		else:
			aantal = 1
		return aantal

	def setLight(self, value):
		if (value == 1):
			self.bus.write_byte_data(self.address, 1, 1)
		else:
			self.bus.write_byte_data(self.address, 1, 0)

	def doCount(self):
		self.bus.write_byte_data(self.address, 0, 1)
		time.sleep(.5)

	def doBoil(self):
		if (self.showtemp == 0):
			self.showtemp = 1
			self.bus.write_byte_data(self.address, 2, 1)
		self.pi.write(15, 0)

	def stopBoil(self):
		if (self.showtemp == 1):
			self.showtemp = 0
			self.bus.write_byte_data(self.address, 2, 0)
		self.pi.write(15, 1)

	def doPump(self):
		self.pi.write(18, 0)

	def stopPump(self):
		self.pi.write(18, 1)

	def doGrind(self):
		self.pi.write(14, 0)

	def stopGrind(self):
		self.pi.write(14, 1)

	def getDorst(self):
		global pompteller
		water_low = self.pi.read(4)
		pomptijd = self.getPomptijd()
		if (pomptijd > 60 or pompteller == 0) and water_low == 1:
			return 1
		else:
			return 0

	def getTemperature(self):
		return self.bus.read_byte_data(self.address, 1)

	def stopAll(self):
		self.stopBoil()
		self.stopPump()
		self.stopGrind()

	def getStateSwitch(self):
		return self.pi.read(27) * 2 + self.pi.read(17)
