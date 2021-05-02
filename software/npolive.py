import httplib2, re, time, datetime


# k1mvl holb3d4vveruvmco 63930

class NPOLive:
	def __init__(self, arg_channel):
		self.kanaal = str(arg_channel)

	def getUrl(self):
		http = httplib2.Http(disable_ssl_certificate_validation=True)
		info, response = http.request(
			"http://ida.omroep.nl/npoplayer/i.js?s=http://www.npo.nl/live/npo-%s" % (self.kanaal))
		if info['status'] == '200':
			# response = "(function(npoplayer){ npoplayer.token = \"aa09u5i04o4qfjdtitc16i3394\"; }(npoplayer));"
			p = re.compile('token = \"([a-zA-Z0-9]*)\"')
			token = p.findall(response)[0]
			print("Complete response: " + response)
			print("Token opgehaald: " + token)
			token = self.friemelToken(token)

			# url = "probeer url: " + "http://ida.omroep.nl/aapi/?callback=jQuery18308831475791569496_1428082441201&type=jsonp&stream=http://livestreams.omroep.nl/live/npo/tvlive/ned"+channel+"/ned"+channel+".isml/ned"+channel+"-audio=128000-video=700000.m3u8&token=%s&version=4.0" % (token)
			# GET /aapi/?callback=jQuery18306757661136888681_1440684352682&type=jsonp&stream=http://livestreams.omroep.nl/live/npo/tvlive/ned1/ned1.isml/ned1.m3u8&token=8i0n188o7l6cgibiub22s422r3&version=5.1.0&_=1440684354971 HTTP/1.1\r\n

			url = "http://ida.omroep.nl/aapi/?callback=jQuery18306757661136888681_1440684352682&type=jsonp&stream=http://livestreams.omroep.nl/live/npo/tvlive/ned" + self.kanaal + "/ned" + self.kanaal + ".isml/ned" + self.kanaal + ".m3u8&token=%s&version=5.1.0&_=%d" % (
			token, int(time.mktime(datetime.datetime.now().timetuple())) * 1000 - 3504)
			# url = "http://ida.omroep.nl/aapi/?callback=jQuery18306757661136888681_1440684352682&type=jsonp&stream=http://livestreams.omroep.nl/live/npo/tvlive/ned"+channel+"/ned"+channel+".isml/ned"+channel+"-audio=128000-video=700000.m3u8&token=%s&version=5.1.0&_=%d"
			print("probeer url: " + url)

			info, response = http.request(url)
			if info['status'] == '200':
				# response = 'jQuery18308831475791569496_1428082441201({"success":true,"stream":"http:\/\/livestreams.omroep.nl\/live\/npo\/tvlive\/ned2\/ned2.isml\/ned2.m3u8?hash=dece5d70e0a9a160e6ebc38d41bd704b&type=jsonp&protection=url"})'
				p = re.compile('"stream":"(http.*?)"}')
				newurl = p.findall(response)[0].replace('\\/', '/')
				print("Stream pre-url: " + newurl)
				info, response = http.request(newurl)
				if info['status'] == '200':
					# response = 'setSource("http:\/\/l2cmde7ca8fc9a00551ed257000000.e0e5ecb0e1884f37.kpnsmoote1a.npostreaming.nl\/d\/live\/npo\/tvlive\/ned2\/ned2.isml\/ned2.m3u8")'
					p = re.compile('setSource\("(http.*?)"\)')
					url = p.findall(response)[0].replace('\\/', '/')
					url = url.replace('ned' + self.kanaal + '.m3u8',
					                  'ned' + self.kanaal + '-audio=128000-video=700000.m3u8')
					print("Stream url: " + url)
					return url

	def friemelToken(self, token):
		print(token)
		token1 = token[:5]
		token2 = token[5:21]
		token3 = token[21:]
		# print token1 + '-' + token2 + '-' + token3
		n = 0
		a = 0
		b = 0
		res = ''
		for i, c in enumerate(token2):
			g = -1
			try:
				g = int(c)
			except Exception:
				g = -1
			if g > -1:
				n = n + 1
				if n == 1:
					a = i
				if n == 2:
					b = i
			if n > 1:
				res = token1 + token2[:a] + token2[b] + token2[a + 1:b] + token2[a] + token2[b + 1:] + token3
				break
		print(res)
		return res
