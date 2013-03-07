# -*- coding: utf-8 *-*

from sys import stdout#, stderr#for statusBar

def statusBar(step, total, bar_len):
	'''print a statusbar like:
[===o----] 40%
'''
	norm=100/total
	step *= norm
	step = int(step)
	increment = 100/bar_len
	n = (step / increment)
	m = bar_len - n
	stdout.write("\r[" + "="*n +"o" +  "-"*m + "]" +  str(step) + "%")
	stdout.flush()
