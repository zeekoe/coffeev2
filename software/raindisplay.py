import pygame, datetime, httplib2, io
from lxml import html

class RainDisplay:
	def __init__(self, scherm1, myhal1):
		self.scherm = scherm1
		

	def update(self):
		font = pygame.font.Font(None, 20)
	
		text = font.render(datetime.datetime.now().strftime("%H:%M"),1, (0,0,0))
		self.scherm.blit(text,(444,2))


		http = httplib2.Http(timeout=5)
		resp, content = http.request('http://xml.buienradar.nl/')
		tree = html.fromstring(content)
		temperature = tree.xpath('//*[@id="6260"]/temperatuurgc')[0].text
		wind = tree.xpath('//*[@id="6260"]/windrichting')[0].text + ' ' + tree.xpath('//*[@id="6260"]/windsnelheidbf')[0].text
		resp, content = http.request('http://api.buienradar.nl/image/1.0/RadarMapNL?w=256&h=236')
		imgfile = io.BytesIO(content)
		img = pygame.image.load(imgfile)
		self.scherm.blit(img,(0,0))
		text = font.render(temperature,1, (0,0,0))
		self.scherm.blit(text,(300,150))
		text = font.render(wind,1, (0,0,0))
		self.scherm.blit(text,(300,170))

