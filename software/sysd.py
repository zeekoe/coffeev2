import httplib2, time, afvalwijzer, socket, os, datetime
from npolive import NPOLive


class SysD:
	def __init__(self, kdisplay, myhal1):
		self.http = httplib2.Http(timeout=2)
		self.http.follow_redirects = False

		self.ticker = 0
		self.cdState = 0
		self.mountState = 0
		self.mountCountDown = 0
		self.tvState = 0
		self.tvCountDown = 0

		self.setterTime = time.localtime()
		self.editingTime = ""
		self.subMode = 0
		self.kdisplay = kdisplay
		self.myhal = myhal1

	def setSubMode(self,mode):
		self.subMode = mode
	def update(self):
		if self.subMode == 0:
			if(self.ticker % 4 == 0):
				if self.tvCountDown > 0:
					self.tvCountDown -= 1
				try:
					self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					self.sock.settimeout(0.1)
					self.sock.connect(('192.168.1.8', 80))
					#self.sock.shutdown(socket.SHUT_RDWR)
					self.sock.close()
					self.sock = None
					self.cdState = 1
				except socket.error as msg:
					print (msg)
					self.cdState = 0
					#resp, content = self.http.request("http://192.168.1.9/ping.html")
					#print resp,content
			aantal = self.myhal.getAantal()
			self.kdisplay.text_line("1. Muziek fixen")
			self.kdisplay.text_line("2. Koffiemachine uitzetten")
			self.kdisplay.text_line(str(aantal))
	def doAction(self):
		aantal = self.myhal.getAantal()
		print( self.subMode)
		if self.subMode == 0:
			if(aantal == 1):
					os.system("sudo service snapclient restart")
			if(aantal == 2):
					print ("shutting down")
					os.system("sync")
					os.system("sudo shutdown -h now")
#                   if(aantal == 5):
#                       self.subMode = 1
			if(aantal == 3 or aantal == 4 or aantal == 5):
					if self.tvState != 0 or self.tvCountDown > 0:
							print (os.system("killall omxplayer.bin"))
							print ("killing omx")
							self.tvState = 0
							self.tvCountDown = 1
							return
			#npo = NPOLive(aantal - 2)
			#url = npo.getUrl()
			#if ("\"" not in url) and ("http" in url):
			self.tvState = aantal - 2
			url = 'http://localhost/npo.php?kanaal=' + str(self.tvState)
			print (url)
			os.system("omxplayer --win 0,0,720,480 --live \""+url+"\" &")
