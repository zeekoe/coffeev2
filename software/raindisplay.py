import pygame, datetime, httplib2, io
from lxml import html

class RainDisplay:
	def __init__(self, scherm1, myhal1):
		self.scherm = scherm1
		self.getFromWeb();

	def update(self):
		font = pygame.font.Font(None, 20)
		text = font.render(datetime.datetime.now().strftime("%H:%M"),1, (0,0,0))
		self.scherm.blit(text,(444,2))
		temperature = self.tree.xpath('//*[@id="6260"]/temperatuurgc')[0].text
		wind = self.tree.xpath('//*[@id="6260"]/windrichting')[0].text + ' ' + self.tree.xpath('//*[@id="6260"]/windsnelheidbf')[0].text
		self.scherm.blit(self.img,(0,0))
		text = font.render(temperature,1, (0,0,0))
		self.scherm.blit(text,(300,150))
		text = font.render(wind,1, (0,0,0))
		self.scherm.blit(text,(300,170))

	def getFromWeb(self):
		print("Getting info from buienradar")
		http = httplib2.Http(timeout=5)
		resp, content = http.request('http://xml.buienradar.nl/')
		self.tree = html.fromstring(content)
		resp, content = http.request('http://api.buienradar.nl/image/1.0/RadarMapNL?w=256&h=236')
		self.imgfile = io.BytesIO(content)
		self.img = pygame.image.load(self.imgfile)

