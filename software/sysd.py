import os

class SysD:
	def __init__(self, kdisplay, myhal1):
		self.kdisplay = kdisplay
		self.myhal = myhal1

	def update(self):
		aantal = self.myhal.getAantal()
		self.kdisplay.text_line("1. Muziek fixen")
		self.kdisplay.text_line("2. Koffiemachine uitzetten")
		self.kdisplay.text_line(str(aantal))
	def doAction(self):
		aantal = self.myhal.getAantal()
		if(aantal == 1):
				os.system("sudo service snapclient restart")
		if(aantal == 2):
				print ("shutting down")
				os.system("sync")
				os.system("sudo shutdown -h now")