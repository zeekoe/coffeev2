import pygame, datetime
from avt import avt
from local_settings import username, password

class NSDisplay:
	def __init__(self, scherm1, myhal1):
		self.avt = avt(username, password)
		self.tickcounter = 0
		self.scherm = scherm1
		#print(pygame.font.get_fonts())
		self.spoorVak = pygame.Surface((26,26),pygame.SRCALPHA,32)
		pygame.draw.rect(self.spoorVak,(255,255,255),(0,0,25,25))
		pygame.draw.rect(self.spoorVak,(255,255,255,0),(0,0,4,4))
		pygame.draw.line(self.spoorVak,(0,0,100),(4,0),(25,0))
		pygame.draw.line(self.spoorVak,(0,0,100),(25,0),(25,25))
		pygame.draw.line(self.spoorVak,(0,0,100),(25,25),(0,25))
		pygame.draw.line(self.spoorVak,(0,0,100),(0,25),(0,4))
		pygame.draw.line(self.spoorVak,(0,0,100),(0,4),(4,4))
		pygame.draw.line(self.spoorVak,(0,0,100),(4,4),(4,0))
		self.spoorVak.convert_alpha()
		nsblauw = (0, 0, 100)
		self.headerVak = pygame.Surface((480,17))
		font = pygame.font.Font(None, 17)
		pygame.draw.rect(self.headerVak, (213,229,255), (0,0,480,17),0)
		text = font.render("Vertrek",1, nsblauw)
		self.headerVak.blit(text,(10,2))
		text = font.render("Naar / Opmerkingen",1, nsblauw)
		self.headerVak.blit(text,(70,2))
		text = font.render("Spoor",1, nsblauw)
		self.headerVak.blit(text,(250-3,2))
		text = font.render("Trein",1, nsblauw)
		self.headerVak.blit(text,(290,2))
		pygame.draw.rect(self.headerVak, nsblauw, (430,0,60,17),0)
		
		try:
			self.tijden = self.avt.fetchandparse('uto')
		except Exception as e:
			print ("Fout bij ophalen tijden: " + str(e))
			return
		#for trein in self.tijden:
		#	print(trein.vertrektijd.strftime("%H:%M"),trein.vertrekspoor,trein.eindbestemming,trein.vertrekvertragingtekst,trein.vertrekvertraging)
		
		

	def update(self):
		self.tickcounter += 1
		if(self.tickcounter % 120 == 0):
			print ("opnieuw ophalen") # elke 30 sec
			try:
				self.tijden = self.avt.fetchandparse('uto')
			except Exception as e:
				print ("Fout bij ophalen tijden: " + str(e))
				return

		
		font = pygame.font.Font(None, 20)
		font18 = pygame.font.Font(None, 18)
		font24 = pygame.font.Font(None, 26)
		
		nsblauw = (0, 0, 100)
		self.scherm.blit(self.headerVak,(0,0))
		text = font.render(datetime.datetime.now().strftime("%H:%M"),1, (255,255,255))
		self.scherm.blit(text,(444,2))
	
		
		for i in range(0,6):
			if i % 2 == 0:
				red = 255
				green = 255
			else:
				red = 213
				green = 229
			pygame.draw.rect(self.scherm, (red,green,255), (0,i * 31+17,480,31),0)
		
		i = 0
		for trein in self.tijden:
			if i < 7:
				ypos = i * 31 + 18
				text = font24.render(trein.vertrektijd.strftime("%H:%M"), 1, nsblauw)
				self.scherm.blit(text, (10, ypos))
				text = font.render(trein.eindbestemming, 1, nsblauw)
				self.scherm.blit(text, (70, ypos+1))
				self.scherm.blit(self.spoorVak, (250,ypos+2))
				text = font24.render(trein.vertrekspoor, 1, nsblauw)
				self.scherm.blit(text, (250+9, ypos + 6))
				text = font.render(trein.treinsoort, 1, nsblauw)
				if(trein.vertrekvertragingtekst != ""):
					self.scherm.blit(text, (290, ypos))
					text = font18.render(trein.vertrekvertragingtekst, 1, (255, 255, 255))
					pygame.draw.rect(self.scherm, nsblauw, (290,ypos + 16,480-290,14),0)
					self.scherm.blit(text, (290, ypos + 16))
				else:
					self.scherm.blit(text, (290, ypos+7))
			i += 1
