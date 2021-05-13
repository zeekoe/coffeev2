import pygame
from pygame import Surface
from kwidgets import KProgressBar
from random import randrange
KOFFIEBRUIN = (102, 41, 18)

class KDisplay:
	def __init__(self, isReal):
		pygame.init()
		if isReal:
			self.screen = pygame.display.set_mode((480, 236), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
		else:
			self.screen = pygame.display.set_mode((480, 236))
		pygame.display.set_caption('Koffie!')
		pygame.mouse.set_visible(0)
		pygame.mixer.quit()  # this saves >25% CPU...
		self.clock = pygame.time.Clock()

		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		# background.fill((250, 250, 250))
		self.plaatje = pygame.image.load('/var/www/scherm.png')
		self.plaatje.convert()
		self.background.blit(self.plaatje, (0, 0))

		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()
		pass

	def clear(self):
		self.background.fill((250, 250, 250))
		pass

	def update(self):
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()
		pass

	def draw_background(self):
		self.background.blit(self.plaatje, (0, 0))

	def tick(self):
		self.clock.tick(4)  # screen refresh rate / clock tick are fixed to 4 FPS
		pass

	def get_key(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				print("Key: ", event.key)
				if event.key == pygame.K_1:
					return '1'
				elif event.key == pygame.K_2:
					return '2'
				elif event.key == pygame.K_3:
					return '3'
				elif event.key == pygame.K_4:
					return '4'
				elif event.key == pygame.K_5:
					return '5'
				elif event.key == pygame.K_q:
					return 'q'
				elif event.key == pygame.K_w:
					return 'w'
				elif event.key == pygame.K_d:
					return 'd'
				elif event.key == pygame.K_SPACE:
					return ' '


class KoffieKorrel:  # drawing of random coffee dust
	def __init__(self, scherm1, myhal1):
		self.scherm = scherm1
		self.myhal = myhal1
		self.korrel = pygame.Surface((3, 3), pygame.SRCALPHA, 32)
		pygame.draw.line(self.korrel, KOFFIEBRUIN, (0, 1), (2, 1))
		pygame.draw.line(self.korrel, KOFFIEBRUIN, (1, 0), (1, 2))
		self.korrel.convert_alpha(self.scherm)

	def update(self):
		maalteller = self.myhal.getMaalteller()
		if (maalteller > 0):
			self.scherm.blit(self.korrel, (100 + randrange(-5, 5), 100 + randrange(-15, 18)))
			self.scherm.blit(self.korrel, (100 + randrange(-5, 5), 100 + randrange(-15, 18)))
			self.scherm.blit(self.korrel, (100 + randrange(-5, 5), 100 + randrange(-15, 18)))


class Pijltjes:  # moving arrows while pumping (needs improvement)
	def __init__(self, scherm1, myhal1):
		self.scherm = scherm1
		self.myhal = myhal1
		self.pijl = pygame.Surface((9, 9), pygame.SRCALPHA, 32)
		pygame.draw.line(self.pijl, (0, 0, 0), (0, 5), (5, 0), 3)
		pygame.draw.line(self.pijl, (0, 0, 0), (0, 5), (5, 9), 3)
		self.pijl.convert_alpha()
		self.cnt = 0

	def update(self, zettijd):
		if zettijd == 0:
			return
		if self.myhal.getDorst() == 0:
			self.cnt = (self.cnt + 1) % 3
		self.scherm.blit(self.pijl, (300 - 2 * self.cnt, 199))

class ProgressCoffee:
	def __init__(self, scherm : Surface):
		self.bar = KProgressBar(scherm, 26, 86, 18, 127, 1000)

	def update(self, param):
		self.bar.update(param)

	def setMaxval(self, max_val):
		self.bar.setMaxval(max_val)


class ProgressWater:
	def __init__(self, scherm : Surface):
		self.bar = KProgressBar(scherm, 340, 19, 18, 127, 1000)

	def update(self, param):
		self.bar.update(param)

	def setMaxval(self, max_val):
		self.bar.setMaxval(max_val)


class TemperatureView:  # rectangle changes from blue to red
	def __init__(self, scherm : Surface, koffiezetter):
		self.koffiezetter = koffiezetter
		self.scherm = scherm

	def update(self):
		font2 = pygame.font.Font(None, 72)
		tmp = self.koffiezetter.myhal.getTemperature()
		red = tmp * 2.55
		if red > 254:
			red = 254
		blue = 255 - red

		temperature_color = (red, 0, blue)
		pygame.draw.rect(self.scherm, temperature_color, (217, 100, 18, 50), 0)
		if self.koffiezetter.myhal.getDorst() == 1:
			self.koffiezetter.myhal.setLight(1)
			text = font2.render("!", 0, (255, 10, 10))
			self.scherm.blit(text, (430, 130))
		else:
			self.koffiezetter.myhal.setLight(0)
		aantal_koppen = self.koffiezetter.myhal.getAantal()
		if len(self.koffiezetter.bezig) != 0:
			aantal_koppen = self.koffiezetter.aantal_koppen
		text = font2.render(str(aantal_koppen), 0, (255, 255, 255))
		self.scherm.blit(text, (105, 156))
