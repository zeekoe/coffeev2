from lxml import html
import httplib2, re, datetime,  pygame
from datetime import date
from local_settings import afval_url

class afvalwijzer:
	def __init__(self):
		self.fullSprite = pygame.Surface((40*2+10, 64))
		self.fullSprite = self.fullSprite.convert()
		self.fullSprite.fill((250, 250, 250))
		print "afval"
	def getafval(self):
		global afval_url
		http = httplib2.Http(timeout=5)
		resp, content = http.request(afval_url)
		tree = html.fromstring(content)
		items = tree.xpath('/html/body/div/div[4]/section/div/div//a/p | /html/body/div/div[4]/section/div/div//p')
		p = re.compile('^[a-z]*?\s')

		dichtstbij = ''
		dagen = 0
		cntr = 0
		for item in items:
			dichtstbij = item.attrib['class']
			if dichtstbij == 'kerstbomen':
				continue
			dag = p.sub('',item.text)
			if '2016' in dag:
				continue
			if 'januari' in dag:
				dag2 = datetime.date(2017,1,int(dag.replace(' januari 2017','')))
			if 'februari' in dag:
				dag2 = datetime.date(2017,2,int(dag.replace(' februari 2017','')))
			if 'maart' in dag:
				dag2 = datetime.date(2017,3,int(dag.replace(' maart 2017','')))
			if 'april' in dag:
				dag2 = datetime.date(2017,4,int(dag.replace(' april 2017','')))
			if 'mei' in dag:
				dag2 = datetime.date(2017,5,int(dag.replace(' mei 2017','')))
			if 'juni' in dag:
				dag2 = datetime.date(2017,6,int(dag.replace(' juni 2017','')))
			if 'juli' in dag:
				dag2 = datetime.date(2017,7,int(dag.replace(' juli 2017','')))
			if 'augustus' in dag:
				dag2 = datetime.date(2017,8,int(dag.replace(' augustus 2017','')))
			if 'september' in dag:
				dag2 = datetime.date(2017,9,int(dag.replace(' september 2017','')))
			if 'oktober' in dag:
				dag2 = datetime.date(2017,10,int(dag.replace(' oktober 2017','')))
			if 'november' in dag:
				dag2 = datetime.date(2017,11,int(dag.replace(' november 2017','')))
			if 'december' in dag:
				dag2 = datetime.date(2017,12,int(dag.replace(' december 2017','')))
			dagen = (dag2 - date.today()).days
			if dagen >= 0:
				sprite = self.makeSprite(dichtstbij, dagen)
				cntr+= 1
				if cntr == 2:
					self.fullSprite.blit(sprite, (50, 0))
					break
				else:
					self.fullSprite.blit(sprite, (0, 0))
		return self.fullSprite
	def makeSprite(self, type, dagen):
		if type == 'pmd':
			sprite = pygame.image.load('/var/www/plastic.png')
		elif type == 'papier':
			sprite = pygame.image.load('/var/www/papier.png')
		elif type == 'gft':
			sprite = pygame.image.load('/var/www/gft.png')
		else:
			print "Onbekend afvaltype `" , type , "`"
		sprite.convert()
		print 'afvalsprite klaar'
		font = pygame.font.Font(None, 40)
		text = font.render(str(dagen), 0, (255, 255, 255))
		sprite.blit(text, (11,28))
		return sprite
