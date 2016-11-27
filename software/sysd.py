import httplib2, time, afvalwijzer, socket, os, pygame,  datetime
from npolive import NPOLive


class SysD:
	def __init__(self, scherm1, myhal1):
		self.http = httplib2.Http(timeout=2)
		self.http.follow_redirects = False
		
		self.ticker = 0
		self.cdState = 0
		self.mountState = 0
		self.mountCountDown = 0
		self.tvState = 0
		self.tvCountDown = 0
		
		self.setterTime = time.localtime()
		self.editingTime = "";
		self.subMode = 0
		self.scherm = scherm1
		self.myhal = myhal1

		try:
			afvalw = afvalwijzer.afvalwijzer()
			self.sprite = afvalw.getafval()
		except Exception, e:
			print e
		
        def setSubMode(self,mode):
            self.subMode = mode
	def update(self):
            if self.subMode == 0:
		if(self.ticker % 4 == 0):
			if self.tvCountDown > 0:
				self.tvCountDown -= 1
			if self.mountCountDown > 0:
				self.mountCountDown -= 1
				print 'mountcountdown', self.mountCountDown
			try:
				self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.sock.settimeout(0.1)
				self.sock.connect(('192.168.1.8', 80))
				#self.sock.shutdown(socket.SHUT_RDWR)
				self.sock.close()
				self.sock = None
				self.cdState = 1
			except socket.error, msg:
				print msg
				self.cdState = 0
			#resp, content = self.http.request("http://192.168.1.9/ping.html")
			#print resp,content
			if os.system("mount |grep music") == 0:
				self.mountState = 1
			else:
				self.mountState = 0
		font = pygame.font.Font(None, 20)
		if hasattr(self,'sprite'):
			self.scherm.blit(self.sprite, (10,10))
		if(self.cdState == 0):
			text = font.render("CD-spelercomputer: uit", 0, (10, 10, 10))
			self.scherm.blit(text, (150,15))
			if(self.mountState == 1):
				try:
					os.system("unmounter.sh")
				except Exception, e:
					print e
		else:
			text = font.render("CD-spelercomputer: aan", 0, (10, 10, 10))
			self.scherm.blit(text, (150,15))
			if(self.mountState == 0):
				text = font.render("Muziek niet beschikbaar op de koffiemachine.", 0, (10, 10, 10))
				try:
					if self.mountCountDown < 1:
						os.system("mounter.sh")
				except Exception, e:
					print e
			else:
				text = font.render("Muziek beschikbaar op de koffiemachine!", 0, (10, 10, 10))
			self.scherm.blit(text, (150,45))
		aantal = self.myhal.getAantal()
		text = font.render("1. CD-spelercomputer uitzetten", 0, (10, 10, 10))
		self.scherm.blit(text, (150,75))
		text = font.render("2. Koffiemachine uitzetten", 0, (10, 10, 10))
		self.scherm.blit(text, (150,105))
		text = font.render("3. Nederland 1", 0, (10, 10, 10))
		self.scherm.blit(text, (150,135))
		text = font.render("4. Nederland 2", 0, (10, 10, 10))
		self.scherm.blit(text, (150,165))
		text = font.render("5. Nederland 3", 0, (10, 10, 10))
		self.scherm.blit(text, (150,195))
		text = font.render(">",0, (10, 10, 10))
		self.scherm.blit(text, (140,45+aantal*30))
		text = font.render(time.strftime("%d / %m, %H:%M"),0, (10,10,10))
                self.scherm.blit(text, (390,5))
            elif self.subMode == 1:
                font = pygame.font.Font(None, 30)
                font20 = pygame.font.Font(None, 20)
                d = font.render(time.strftime("%d / %m", self.setterTime),0, (10,10,10))
                H = font.render(time.strftime("%H", self.setterTime),0, (10,10,10))
                dp = font.render(":",0, (10,10,10))
                M = font.render(time.strftime("%M", self.setterTime),0, (10,10,10))
                tickDisplay = 1
                if self.tvCountDown > 0:
                    self.tvCountDown -= 1
                if(self.ticker % 4 == 0):
                    tickDisplay = 0
                if(self.editingTime != 'd' or tickDisplay == 1):
                    self.scherm.blit(d, (100,45))
                if(self.editingTime != 'H' or tickDisplay == 1):
                    self.scherm.blit(H, (180,45))
                self.scherm.blit(dp, (203,45))
                if(self.editingTime != 'M' or tickDisplay == 1):
                    self.scherm.blit(M, (210,45))
                
                text = font20.render("Nu: " + time.strftime("%d / %m, %H:%M"),0, (10,10,10))
                self.scherm.blit(text, (100,70))
                if(self.editingTime == ''):
                    text = font20.render("4 = bewerken, 2 = terug",0, (10,10,10))
                    self.scherm.blit(text, (100,100))
                else:
                    text = font.render("-5     -1    4=ok    +1     +5",0, (10,10,10))
                    self.scherm.blit(text, (100,100))
            self.ticker += 1
	def doAction(self):
		aantal = self.myhal.getAantal()
		print self.subMode
		if self.subMode == 0:
                    if(aantal == 1):
                            try:
                                    self.mountCountDown = 20
                                    os.system("unmounter.sh")
                                    resp, content = self.http.request("http://192.168.1.8/index.php?shutdown")
                                    print resp,content
                            except Exception, e:
                                    print e
                    if(aantal == 2):
                            print "shutting down"
                            os.system("sync")
                            os.system("sudo shutdown -h now")
#                   if(aantal == 5):
#                       self.subMode = 1
                    if(aantal == 3 or aantal == 4 or aantal == 5):
                            if self.tvState != 0 or self.tvCountDown > 0:
                                    print os.system("killall omxplayer.bin")
                                    print "killing omx"
                                    self.tvState = 0
                                    self.tvCountDown = 1
                                    return
			    #npo = NPOLive(aantal - 2)
			    #url = npo.getUrl()
			    #if ("\"" not in url) and ("http" in url):
			    self.tvState = aantal - 2
			    url = 'http://localhost/npo.php?kanaal=' + str(self.tvState)
			    print url
			    os.system("omxplayer --win 0,0,720,480 --live \""+url+"\" &")
                elif self.subMode == 1:
                    n = 0
                    if self.tvCountDown > 0:
                        return
                    if aantal == 4:
                        self.tvCountDown = 4
                        if self.editingTime == '':
                            self.editingTime = 'd'
                        elif self.editingTime == 'd':
                            self.editingTime = 'H'
                        elif self.editingTime == 'H':
                            self.editingTime = 'M'
                        elif self.editingTime == 'M':
                            self._linux_set_time(self.setterTime)
                            self.editingTime = ''
                            self.subMode = 0
                            self.tvCountDown = 0
                    if aantal == 5:
                        n=-5
                    if aantal == 3:
                        n=-1
                    if aantal == 1:
                        n=1
                    if aantal == 2:
                        if self.editingTime == '':
                            self.subMode = 0
                            self.tvCountDown = 0
                        else:
                            n=5
                    if aantal != 4:
                        if self.editingTime == 'd':
                            self.setterTime = (datetime.datetime(*self.setterTime[0:6]) + datetime.timedelta(days=n)).timetuple()
                        if self.editingTime == 'M':
                            self.setterTime = (datetime.datetime(*self.setterTime[0:6]) + datetime.timedelta(minutes=n)).timetuple()
                        if self.editingTime == 'H':
                            self.setterTime = (datetime.datetime(*self.setterTime[0:6]) + datetime.timedelta(hours=n)).timetuple()
        
        def _linux_set_time(self,time_tuple):
            print os.system("/bin/date -s @%d" % int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) ))
            
            return
