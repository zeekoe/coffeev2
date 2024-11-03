#!/usr/bin/python3
import curses
from curses.textpad import Textbox, rectangle

def main(stdscr):
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
	stdscr.clear()
	stdscr.addstr(0, 0, "Current mode: Typing mode", curses.A_REVERSE)
	stdscr.addstr("Pretty text", curses.color_pair(1))
	stdscr.refresh()
	window = curses.newwin(6, 22, 2, 1)
	window.border()
	stdscr.refresh()

	window.keypad(True)

	while True:
		try:
			character = -1
			while (character < 0):
				character = window.getch()
		except:
			break
		if chr(character) == 'q':
			break
		elif chr(character) == 'w':
			window.addstr('w')
			stdscr.refresh()


curses.wrapper(main)