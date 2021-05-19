from random import randrange
KOFFIEBRUIN = (102, 41, 18)

import curses
from curses.textpad import Textbox, rectangle
import time, datetime


class KDisplay:
	def __init__(self, isReal):
		print("init kdisplay")
		time.sleep(1)
		self.stdscr = curses.initscr()
		curses.start_color()
		self.stdscr.clear()
		self.stdscr.refresh()
		self.background = curses.newwin(6, 22, 2, 1)
		self.stdscr.refresh()

		self.background.nodelay(True)
		self.background.keypad(True)
		pass

	def clear(self):
		self.background.clear()
		pass

	def update(self):
		self.stdscr.refresh()
		pass

	def draw_background(self):
		self.background.clear()
		pass

	def tick(self):
		time.sleep(0.25)
		pass

	def get_key(self):
		character = self.background.getch()
		if character == -1:
			return '-'
		return chr(character)

	def shutdown(self):
		curses.nocbreak()
		self.stdscr.keypad(False)
		curses.echo()
		curses.endwin()

	def text_line(self, text):
		self.background.addstr(text + "\n")


class KoffieKorrel:  # drawing of random coffee dust
	def __init__(self, scherm1, myhal1):
		self.scherm = scherm1
		self.myhal = myhal1
		self.korrel = None

	def update(self):
		pass

class Pijltjes:  # moving arrows while pumping (needs improvement)
	def __init__(self, scherm1, myhal1):
		pass

	def update(self, zettijd):
		pass

class ProgressCoffee:
	def __init__(self, scherm):
		self.max_val = 1000
		self.window = scherm
		pass
		# self.bar = KProgressBar(scherm, 26, 86, 18, 127, 1000)

	def update(self, param):
		self.window.addstr("koffie: ")
		self.window.addstr(str(int(100 * param / self.max_val)))
		self.window.addstr("\n")
		pass

	def setMaxval(self, max_val):
		self.max_val = max_val
		pass


class ProgressWater:
	def __init__(self, scherm):
		self.max_val = 1000
		self.window = scherm
		pass

	def update(self, param):
		self.window.addstr("water: ")
		self.window.addstr(str(int(100 * param / self.max_val)))
		self.window.addstr("\n")
		pass

	def setMaxval(self, max_val):
		self.max_val = max_val
		pass


class TemperatureView:  # rectangle changes from blue to red
	def __init__(self, scherm, koffiezetter):
		self.koffiezetter = koffiezetter
		self.window = scherm

	def update(self):
		tmp = self.koffiezetter.myhal.getTemperature()
		self.window.addstr(str(tmp))
		self.window.addstr(" C ")
		red = tmp * 2.55
		if red > 254:
			red = 254
		blue = 255 - red

		temperature_color = (red, 0, blue)
		# pygame.draw.rect(self.scherm, temperature_color, (217, 100, 18, 50), 0)
		if self.koffiezetter.myhal.getDorst() == 1:
			self.koffiezetter.myhal.setLight(1)
			self.window.addstr("!")
			# text = font2.render("!", 0, (255, 10, 10))
			# self.scherm.blit(text, (430, 130))
		else:
			self.koffiezetter.myhal.setLight(0)
		aantal_koppen = self.koffiezetter.myhal.getAantal()
		if len(self.koffiezetter.bezig) != 0:
			aantal_koppen = self.koffiezetter.aantal_koppen
		self.window.addstr(str(aantal_koppen))
		self.window.addstr(" kop ")
		self.window.addstr(datetime.datetime.now().strftime("%H:%M:%S"))
		self.window.addstr("\n")
