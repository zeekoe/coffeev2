from lxml import html
import httplib2, re, datetime,  pygame
from datetime import date
from local_settings import afval_url

class afvalwijzer:
	def __init__(self):
		self.fullSprite = pygame.Surface((40*2+10, 64))
		self.fullSprite = self.fullSprite.convert()
		self.fullSprite.fill((250, 250, 250))
		print ("afval")
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
			if 'januari' in dag:
				dag2 = datetime.date(2019,1,int(dag.replace(' januari','')))
			if 'februari' in dag:
				dag2 = datetime.date(2019,2,int(dag.replace(' februari','')))
			if 'maart' in dag:
				dag2 = datetime.date(2019,3,int(dag.replace(' maart','')))
			if 'april' in dag:
				dag2 = datetime.date(2019,4,int(dag.replace(' april','')))
			if 'mei' in dag:
				dag2 = datetime.date(2019,5,int(dag.replace(' mei','')))
			if 'juni' in dag:
				dag2 = datetime.date(2019,6,int(dag.replace(' juni','')))
			if 'juli' in dag:
				dag2 = datetime.date(2019,7,int(dag.replace(' juli','')))
			if 'augustus' in dag:
				dag2 = datetime.date(2019,8,int(dag.replace(' augustus','')))
			if 'september' in dag:
				dag2 = datetime.date(2019,9,int(dag.replace(' september','')))
			if 'oktober' in dag:
				dag2 = datetime.date(2019,10,int(dag.replace(' oktober','')))
			if 'november' in dag:
				dag2 = datetime.date(2019,11,int(dag.replace(' november','')))
			if 'december' in dag:
				dag2 = datetime.date(2019,12,int(dag.replace(' december','')))
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
			print ("Onbekend afvaltype `" , type , "`")
		sprite.convert()
		print ('afvalsprite klaar')
		font = pygame.font.Font(None, 40)
		text = font.render(str(dagen), 0, (255, 255, 255))
		sprite.blit(text, (11,28))
		return sprite
