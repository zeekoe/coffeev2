import httplib2, datetime, os
from kdisplay import KDisplay, TemperatureView, KoffieKorrel, ProgressCoffee, ProgressWater
import sqlite3 as sqlite
from local_settings import coffee_set_url
import time

zetkoffie = 0


# references:
# 1000 count units = 380 ml
# 1 cup = 220 ml


class Koffiezetter:
	bezig = 0
	bezig_malen = 0
	zettijd = 0
	wachttijd = 0
	knipper = 0

	def __init__(self, scherm1: KDisplay, myhal1):
		self.aantal_koppen = 0
		self.scherm = scherm1
		self.myhal = myhal1
		self.bezig = ''
		self.http = httplib2.Http(timeout=2)
		self.tempv = TemperatureView(self.scherm.background, self)
		self.progress_coffee = ProgressCoffee(self.scherm.background)
		self.progress_water = ProgressWater(self.scherm.background)
		self.kk = KoffieKorrel(self.scherm.background, self.myhal)
		self.programma = []
		self.coffee_set_url = coffee_set_url
		self.do_pre_heat = 0

	def start(self, aantal):
		if len(self.bezig) != 0:
			print("Already started!")
			return
		self.aantal_koppen = aantal
		# AutoBaristaScripts defined; Z = add hot water; M = grind; S = sleep
		if self.aantal_koppen == 1:  # 2274 is the first cup of 175ml instead of 240ml
			self.programma = ['Z6', 'M107', 'Z50', 'S60', 'Z115']  # 50 + 170 = 220
			return
		if self.aantal_koppen == 2:
			self.programma = ['Z6', 'M171', 'Z50', 'S60', 'Z270']  # 50 + 390 = 440
			return
		if self.aantal_koppen == 3:
			self.programma = ['Z6', 'M255', 'Z50', 'S60', 'Z425']  # 50 + 610 = 660
			return
		if self.aantal_koppen == 4:
			self.programma = ['Z6', 'M309', 'Z50', 'S60', 'Z580']  # 60 + 830 = 880
			return
		if self.aantal_koppen == 5:  # ontkalken / descaling
			self.programma = [
				'Z500']  # ['Z100','S50','Z100','S200','Z100','S50','Z100','S10','Z10','S10','Z10','S340','Z400']
			return

	def updateUi(self):  # update all UI elements
		try:
			self.scherm.draw_background()
			self.tempv.update()
			self.progress_coffee.update(self.myhal.getMaalteller())
			self.kk.update()
			if self.zettijd > 0:
				self.progress_water.update(self.zettijd)
			else:
				self.progress_water.update(self.wachttijd)
		except Exception as e:
			self.scherm.shutdown()

	def update(self):  # every 1/4 second, this routine is called
		self.pre_heat()
		if len(self.programma) > 0 and self.bezig != self.programma[0]:
			self.bezig = self.programma[0]
			# first character of program defines action; check what action we are doing now.
			if self.bezig[0] == 'M':
				n = int(self.bezig[1:])
				self.myhal.setMaalteller(n)
				self.progress_coffee.setMaxval(n)
				if self.aantal_koppen != 5:
					self.myhal.doGrind()
			if self.bezig[0] == 'Z':
				n = int(self.bezig[1:])
				self.myhal.setPompteller(n)
				self.progress_water.setMaxval(n)
			if self.bezig[0] == 'S':
				n = int(self.bezig[1:])
				self.wachttijd = n
				self.progress_water.setMaxval(n)

		if len(self.bezig) == 0:  # no actions left? return.
			return

		if self.knipper < 4 or self.myhal.getDorst() == 1:  # fancy light flashing :)
			self.myhal.setLight(1)
		else:
			self.myhal.setLight(0)
		if self.knipper > 8:
			self.knipper = 0
		self.knipper += 1

		maalteller = self.myhal.getMaalteller()

		if self.bezig[0] == 'M' and maalteller < 1:
			self.myhal.stopGrind()
			self.programma.pop(0)  # next script item
			self.myhal.setMaalteller(0)

		if self.bezig[0] == 'Z':
			# font = pygame.font.Font(None, 36)
			# text = font.render("Tijd: " + str(self.zettijd), 1, (10, 10, 10))
			# self.scherm.blit(text, (40,40))
			return self.boilcheck()  # boiling & pumping control gets a separate subroutine

		if self.bezig[0] == 'S':
			self.wachttijd -= 1
			if self.wachttijd < 1:
				self.programma.pop(0)  # next script item

	def pre_heat(self):
		if self.do_pre_heat != 1:
			return
		hour = time.localtime().tm_hour
		if hour not in (6, 7, 8, 9, 13, 14):
			self.do_pre_heat = 0
			return
		temperatuur = self.myhal.getTemperature()

		if temperatuur < 80:
			self.myhal.doBoil()
		else:
			self.myhal.stopBoil()
			self.do_pre_heat = 0

	def boilcheck(self):
		self.zettijd = self.myhal.getPompteller()
		temperatuur = self.myhal.getTemperature()
		# some trial & error control engineering to get water of the right temperature
		# (temperatures are somewhat in degrees celcius, but no accurate calibration is done)
		if (self.zettijd > 0):
			if (temperatuur > 88 or self.zettijd < 30) and self.myhal.getDorst() == 0:
				self.myhal.doPump()
				if self.zettijd > 25:
					self.myhal.doBoil()
			else:
				self.myhal.stopPump()
				if (temperatuur < 93 and self.zettijd > 25):
					self.myhal.doBoil()
				else:
					self.myhal.stopBoil()
		else:
			self.myhal.stopAll()
			self.myhal.setLight(0)
			self.programma.pop(0)  # next script item
			self.bezig = ''
			if len(self.programma) == 0 and self.aantal_koppen != 5:  # finished & not descaling? store # of cups
				try:
					con = sqlite.connect("/home/pi/code/koffiepy/koffie.db", detect_types=sqlite.PARSE_COLNAMES)
					cur = con.cursor()
					cur.execute("insert into koffie(aantal,datum) values(?, ?)",
					            (self.aantal_koppen, datetime.datetime.now()))
					con.commit()
					cur.close()
					con.close()
					os.system("sync")
				except Exception as e:
					print("Error writing to database: " + str(e))

				while self.aantal_koppen > 0:
					self.myhal.doCount()  # physical counter
					self.aantal_koppen -= 1
				try:
					# resp, content = self.http.request("2.php?&aantal=" + str(self.aantal_koppen) + "&datum=" + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
					resp, content = self.http.request(
						self.coffee_set_url)  # ask internet server to pull db change from machine

				except Exception as e:
					print(e)
		return self.zettijd

	def handle_bot_message(self, message):
		if 'cup of coffee' in message.text.lower():
			self.start(1)
		elif 'two cups of coffee' in message.text:
			self.start(2)
		elif message.text.lower() == 'coffee':
			self.start(1)
