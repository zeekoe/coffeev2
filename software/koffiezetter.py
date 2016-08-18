import httplib2, pygame, datetime, time, os
from random import randrange
from pysqlite2 import dbapi2 as sqlite
from kwidgets import KProgressBar
from local_settings import coffee_set_url

KOFFIEBRUIN = (102, 41, 18)
zetkoffie = 0


class Koffiezetter:
	bezig = 0
	bezig_malen = 0
	zettijd = 0
	knipper = 0

	def __init__(self, scherm1, myhal1, botsender):
		self.aantal_koppen = 0
		self.scherm = scherm1
		self.myhal = myhal1
		self.bezig = ''
		self.http = httplib2.Http(timeout=2)
		self.tempv = TemperatureView(self)
		self.kp1 = KProgressBar(self.scherm,26,86,18,127,1000)
		self.kp2 = KProgressBar(self.scherm,340,19,18,127,1000)
		self.kk = KoffieKorrel(self.scherm, self.myhal)
		self.pijl = Pijltjes(self.scherm, self.myhal)
		self.programma = []
		self.coffee_set_url = coffee_set_url
		self.botsender = botsender
	def start(self,aantal):
		if len(self.bezig) != 0:
			print "Already started!"
			return
		self.aantal_koppen = aantal
		maalteller = self.myhal.getMaalteller()
		print("Start " + str(self.aantal_koppen))
		self.botsender("Starting to brew " + str(self.aantal_koppen) + " cups of coffee.",0)
		zt = self.aantal_koppen * 110 + 10
		if self.aantal_koppen == 1:
			self.programma = ['Z8','M135','Z16','S60','Z120'] # 46, 780/783
			return
		if self.aantal_koppen == 2:
			self.programma = ['Z8','M190','Z16','S60','Z220'] # 1325
			return
		if self.aantal_koppen == 3:
			self.programma = ['Z8','M260','Z16','S60','Z290']
			return
		if self.aantal_koppen == 4:
			self.programma = ['Z8','M320','Z16','S60','Z400']
			return
		if self.aantal_koppen == 5: #ontkalken / descaling
			self.programma = ['Z8'] #['Z100','S50','Z100','S200','Z100','S50','Z100','S10','Z10','S10','Z10','S340','Z400']
			return

	def updateUi(self):
		self.tempv.update()
		self.kp1.update(self.myhal.getMaalteller())
		self.kk.update()
		self.kp2.update(self.zettijd)
		self.pijl.update(self.zettijd)

		font = pygame.font.Font(None, 36)
		text = font.render(str(self.myhal.getPompteller()), 0, (10, 10, 10))
		self.scherm.blit(text, (200,15))
	
	def update(self):
		if len(self.programma) > 0 and self.bezig != self.programma[0]:
			self.bezig = self.programma[0]
			if self.bezig[0] == 'M':
				n = int(self.bezig[1:])
				print 'maal: ', n
				self.myhal.setMaalteller(n)
				self.kp1.setMaxval(n)
				if self.aantal_koppen != 5:
					self.myhal.doGrind()
			if self.bezig[0] == 'Z':
				n = int(self.bezig[1:])
				print 'zet: ',n
				self.zettijd = n
				self.kp2.setMaxval(n)
			if self.bezig[0] == 'S':
				n = int(self.bezig[1:])
				print 'wacht: ',n
				self.zettijd = n
				self.kp2.setMaxval(n)

		if len(self.bezig) == 0:
			return

		if self.knipper < 4 or self.myhal.getDorst() == 1:
			self.myhal.setLight(1)
		else:
			self.myhal.setLight(0)
		if self.knipper > 8:
			self.knipper = 0
		self.knipper += 1

		maalteller = self.myhal.getMaalteller()

		if self.bezig[0] == 'M' and maalteller < 1:
			self.myhal.stopGrind()
			self.programma.pop(0)
			self.myhal.setMaalteller(0)

		if self.bezig[0] == 'Z':
			# font = pygame.font.Font(None, 36)
			# text = font.render("Tijd: " + str(self.zettijd), 1, (10, 10, 10))
			# self.scherm.blit(text, (40,40))
			return self.boilcheck()
		
		if self.bezig[0] == 'S':
			self.zettijd -= 1
			if self.zettijd < 1:
				self.programma.pop(0)

	def boilcheck(self):
		print self.bezig, self.zettijd
		temperatuur = self.myhal.getTemperature()
		if(self.zettijd > 0):
			if(temperatuur > 92 or self.zettijd < 10) and self.myhal.getDorst() == 0:
				self.myhal.doPump()
				self.zettijd -= 1
				if self.zettijd > 8:
					self.myhal.doBoil()
			else:
				self.myhal.stopPump()
				if(temperatuur < 97 and self.zettijd > 8):
					self.myhal.doBoil()
				else:
					self.myhal.stopBoil()
		else:
			self.myhal.stopAll()
			self.myhal.setLight(0)
			self.programma.pop(0)
			self.bezig = ''
			if len(self.programma) == 0 and self.aantal_koppen != 5:
				try:
					con = sqlite.connect("/home/pi/code/koffiepy/koffie.db", detect_types=sqlite.PARSE_COLNAMES)
					cur = con.cursor()
					cur.execute("insert into koffie(aantal,datum) values(?, ?)", (self.aantal_koppen, datetime.datetime.now()))
					con.commit()
					cur.close()
					con.close()
                            		os.system("sync")
				except Exception, e:
					print "Error writing to database: " + str(e)
		
				while self.aantal_koppen > 0:
					self.myhal.doCount()
					self.aantal_koppen -= 1
				try:
					#resp, content = self.http.request("2.php?&aantal=" + str(self.aantal_koppen) + "&datum=" + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
					self.botsender("Coffee is finished! Enjoy!",0)
					resp, content = self.http.request(self.coffee_set_url)
				except Exception, e:
					print e
		return self.zettijd
	def handle_bot_message(self, message):
		if 'cup of coffee' in message.text.lower():
			self.start(1)
		else if 'two cups of coffee' in message.text:
			self.start(2)
		else if message.text.lower() == 'coffee':
			self.start(1)

class KoffieKorrel:
	def __init__(self, scherm1, myhal1):
		self.scherm = scherm1
		self.myhal = myhal1
		self.korrel = pygame.Surface((3,3),pygame.SRCALPHA,32)
		pygame.draw.line(self.korrel,KOFFIEBRUIN,(0,1),(2,1))
		pygame.draw.line(self.korrel,KOFFIEBRUIN,(1,0),(1,2))
		self.korrel.convert_alpha()
	def update(self):
		maalteller = self.myhal.getMaalteller()
		if(maalteller > 0):
			self.scherm.blit(self.korrel,(100+randrange(-5,5),100+randrange(-15,18)))
			self.scherm.blit(self.korrel,(100+randrange(-5,5),100+randrange(-15,18)))
			self.scherm.blit(self.korrel,(100+randrange(-5,5),100+randrange(-15,18)))
	

class Pijltjes:
	def __init__(self, scherm1, myhal1):
		self.scherm = scherm1
		self.myhal = myhal1
		self.pijl = pygame.Surface((9,9),pygame.SRCALPHA,32)
		pygame.draw.line(self.pijl,(0,0,0),(0,5),(5,0),3)
		pygame.draw.line(self.pijl,(0,0,0),(0,5),(5,9),3)
		self.pijl.convert_alpha()
		self.cnt = 0
	def update(self,zettijd):
		if zettijd == 0:
			return
		if self.myhal.getDorst() == 0:
			self.cnt = (self.cnt + 1) % 3
		self.scherm.blit(self.pijl,(300-2*self.cnt,199))

class TemperatureView:
	def __init__(self, koffiezetter):
		self.koffiezetter = koffiezetter
	def update(self):
		font = pygame.font.Font(None, 36)
		font2 = pygame.font.Font(None, 72)
		tmp = self.myhal.getTemperature()
		red = tmp*2.55
		if red > 254:
			red = 254
		blue = 255-red

		pygame.draw.rect(koffiezetter.scherm, (red,0,blue), (217,100,18,50),0)
		if koffiezetter.myhal.getDorst() == 1:
			koffiezetter.myhal.setLight(1)
			text = font2.render("!", 0, (255, 10, 10))
			koffiezetter.scherm.blit(text, (430,130))
		else:
			koffiezetter.myhal.setLight(0)
		aantal_koppen = koffiezetter.myhal.getAantal()
		if len(self.koffiezetter.bezig) != 0:
			aantal_koppen = self.koffiezetter.aantal_koppen
		text = font2.render(str(aantal_koppen),0, (255,255,255))
		koffiezetter.scherm.blit(text, (105,156))
