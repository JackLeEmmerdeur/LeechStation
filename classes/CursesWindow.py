import curses


class CursesWindow:

	stdscreen = None

	def __init__(self):
		self.stdscreen = curses.initscr()
		curses.noecho()
		self.stdscreen.keypad(True)

	def clear(self):
		if self.stdscreen is not None:
			self.stdscreen.clear()
			self.stdscreen.refresh()

	def getchar(self):
		if self.stdscreen is not None:
			self.stdscreen.getkey()

	def stop(self):
		if self.stdscreen is not None:
			self.stdscreen.keypad(False)
			curses.echo()
			curses.endwin()

	def draw(self, x, y, thestr):
		if self.stdscreen is not None:
			self.stdscreen.addstr(x, y, thestr)
