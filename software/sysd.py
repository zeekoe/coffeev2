import os

class SysD:
	def __init__(self, kdisplay, myhal1):
		self.kdisplay = kdisplay
		self.myhal = myhal1
		self.myhal.setLight(1)

	def update(self):
		aantal = self.myhal.getAantal()
		self.kdisplay.text_line("1. Muziek fixen")
		self.kdisplay.text_line("2. Koffiemachine uitzetten")
		self.kdisplay.text_line("3. Woonkamerversterker uit")
		self.kdisplay.text_line("4. Woonkamerversterker aan")
		self.kdisplay.text_line(str(aantal))
		self.kdisplay.text_line(self.myhal.uiExtra())
	def doAction(self):
		aantal = self.myhal.getAantal()
		if(aantal == 1):
				os.system("sudo service snapclient restart")
		if(aantal == 2):
				print ("shutting down")
				self.myhal.shutdown()
				os.system("sync")
				os.system("sudo shutdown -h now")
				self.myhal.shutdown()
		if(aantal == 3):
				os.system("wget -O - http://192.168.1.120:8280/amp/off")
		if(aantal == 4):
				os.system("wget -O - http://192.168.1.120:8280/amp/on")

