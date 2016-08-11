from lxml import html
import httplib2, re, datetime
from datetime import date
from local_settings import afval_url

class afvalwijzer:
	def __init__(self):
		print "afval"
	def getafval(self):
		global afval_url
		http = httplib2.Http(timeout=5)
		resp, content = http.request(afval_url)
		tree = html.fromstring(content)
		items = tree.xpath('/html/body/div/div[5]/section/div[2]/div//a/p | /html/body/div/div[5]/section/div[2]/div//p')
		p = re.compile('^[a-z]*?\s')

		dichtstbij = ''
		dagen = 0
		for item in items:
			dichtstbij = item.attrib['class']
			if dichtstbij == 'kerstbomen':
				continue
			dag = p.sub('',item.text)
			if 'januari' in dag:
				dag2 = datetime.date(2016,1,int(dag.replace(' januari','')))
			if 'februari' in dag:
				dag2 = datetime.date(2016,2,int(dag.replace(' februari','')))
			if 'maart' in dag:
				dag2 = datetime.date(2016,3,int(dag.replace(' maart','')))
			if 'april' in dag:
				dag2 = datetime.date(2016,4,int(dag.replace(' april','')))
			if 'mei' in dag:
				dag2 = datetime.date(2016,5,int(dag.replace(' mei','')))
			if 'juni' in dag:
				dag2 = datetime.date(2016,6,int(dag.replace(' juni','')))
			if 'juli' in dag:
				dag2 = datetime.date(2016,7,int(dag.replace(' juli','')))
			if 'augustus' in dag:
				dag2 = datetime.date(2016,8,int(dag.replace(' augustus','')))
			if 'september' in dag:
				dag2 = datetime.date(2016,9,int(dag.replace(' september','')))
			if 'oktober' in dag:
				dag2 = datetime.date(2016,10,int(dag.replace(' oktober','')))
			if 'november' in dag:
				dag2 = datetime.date(2016,11,int(dag.replace(' november','')))
			if 'december' in dag:
				dag2 = datetime.date(2016,12,int(dag.replace(' december','')))
			dagen = (dag2 - date.today()).days
			if dagen >= 0:
				break
		return [dagen,dichtstbij]
