# -*- coding: utf-8 *-*

class _Getch:
	"""Gets a single character from standard input.  Does not echo to the
screen."""
	def __init__(self):
		try:
			self.impl = _GetchWindows()
		except ImportError:
			#try:
			self.impl = _GetchUnix()
		   # except ImportError:
		   #	 self.impl = _GetchMacCarbon()

	def __call__(self): return self.impl()


class _GetchUnix:
	def __init__(self):
		import tty, sys, termios # import termios now or else you'll get the Unix version on the Mac

	def __call__(self):
		import sys, tty, termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch

class _GetchWindows:
	def __init__(self):
		import msvcrt

	def __call__(self):
		import msvcrt
		return msvcrt.getch()

if __name__ == '__main__':
	# to demonstrate functionality:
	# schow pressed keys
	import sys
	print "This module tracks and show the input of your keybord"
	print "Press 's' to stop"
	keyPressed = _Getch()
	while True:
		out = keyPressed()
		print out
		if out == "s":
			sys.exit()
